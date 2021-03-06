import itertools
import os
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from operator import attrgetter

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone

from zsolozsma import models, youtube

SCHEDULE_FUTURE_DAYS = os.getenv('SCHEDULE_FUTURE_DAYS', 3)
TIMEDELTA_TOLERANCE = os.getenv('TIMEDELTA_TOLERANCE', 15)


class BroadcastState:
    Future, Upcoming, Live, Recent, Past, Invalid = range(6)


class ScheduleItem(object):
    name = None
    schedule_hash = None
    date = None
    time = None
    city_slug = None
    city_name = None
    location_slug = None
    location_name = None

    state = None
    style = None

    def __init__(self, schedule, date):
        event = schedule.event
        location = event.location
        city = location.city

        self.name = event.name
        self.schedule_hash = schedule.hash
        self.date = date
        self.time = schedule.time
        self.city_slug = city.slug
        self.city_name = city.name
        self.location_slug = location.slug
        self.location_name = location.name

        self.state = get_broadcast_status(schedule, date)
        self.style = self.__get_style()

    def __get_style(self):
        if (self.state == BroadcastState.Live):
            return 'live'
        elif (self.state == BroadcastState.Upcoming or self.state == BroadcastState.Recent):
            return 'highlight'
        else:
            return 'disabled'


def get_schedule(location_slug=None,
                 liturgy_slug=None,
                 city_slug=None,
                 denomination_slug=None):

    today = timezone.localtime().date()
    validity_end = today + timedelta(days=SCHEDULE_FUTURE_DAYS)
    dates = [(date, date.weekday()) for date in
             [today + timedelta(days=i) for i in range(SCHEDULE_FUTURE_DAYS)]]

    scheduleQuery = models.EventSchedule.objects\
        .select_related('event', 'event__location', 'event__location__city')\
        .filter(event__is_active=True, event__location__is_active=True)\
        .filter(Q(valid_from__lte=validity_end)|Q(valid_from=None))\
        .filter(Q(valid_to__gte=today)|Q(valid_to=None))

    if (location_slug):
        scheduleQuery = scheduleQuery.filter(event__location__slug=location_slug)
    if (liturgy_slug):
        scheduleQuery = scheduleQuery.filter(event__liturgy__slug=liturgy_slug)
    if (city_slug):
        scheduleQuery = scheduleQuery.filter(event__location__city__slug=city_slug)
    if (denomination_slug):
        scheduleQuery = scheduleQuery.filter(event__liturgy__denomination__slug=denomination_slug)

    scheduleQuery = scheduleQuery.filter(day_of_week__in=[d[1] for d in dates])
    days = defaultdict(list)
    for scheduleItem in scheduleQuery:
        days[scheduleItem.day_of_week].append(scheduleItem)

    schedule = [
        scheduleItem for scheduleItem in [
            ScheduleItem(eventSchedule, _date) for (_date, _day) in dates
            for eventSchedule in days[_day]
        ] if scheduleItem.state != BroadcastState.Past
        and scheduleItem.state != BroadcastState.Invalid
    ]

    schedule.sort(key=attrgetter('date', 'time', 'city_name', 'location_name'))

    return schedule


def get_broadcast_status(schedule, date):
    now = timezone.localtime()
    if (now.date() < date):
        return BroadcastState.Future

    event_time = timezone.get_current_timezone().localize(
        datetime.combine(date, schedule.time))

    if (schedule.valid_from and schedule.valid_from > date):
        return BroadcastState.Invalid
    if (schedule.valid_to and schedule.valid_to < date):
        return BroadcastState.Invalid

    difference = now - event_time
    minutes = difference.total_seconds() / 60

    duration = schedule.event.duration or 60

    if (minutes < -TIMEDELTA_TOLERANCE):
        return BroadcastState.Future  # még több, mint 15 perc a kezdésig
    elif (minutes < 0):
        return BroadcastState.Upcoming  # 15 percen belül kezdődik
    elif (minutes < duration):
        return BroadcastState.Live  # éppen tart
    elif (minutes < duration + TIMEDELTA_TOLERANCE):
        return BroadcastState.Recent  # 15 percen belül ért véget
    else:
        return BroadcastState.Past


class BroadcastItem(object):
    def __init__(self, event, broadcast):
        self.event_name = event.name
        self.city_name = event.location.city.name
        self.location_name = event.location.name
        self.liturgy_name = event.liturgy.name

        self.starttime = datetime.combine(broadcast.date,
                                          broadcast.schedule.time)
        self.starttime_label = timezone.get_current_timezone().localize(
            self.starttime)

        self.has_text = bool(broadcast.text_url)
        self.text_url = broadcast.text_url
        self.text_iframe = broadcast.text_iframe

        self.video_embed_url = broadcast.get_video_embed_url()
        self.video_link_url = broadcast.get_video_link_url()
        self.video_iframe = broadcast.video_iframe
        self.video_only = broadcast.is_16_9()


def get_broadcast(schedule, date):
    broadcast = __get_or_create_broadcast(schedule, date)

    broadcast_item = BroadcastItem(schedule.event, broadcast)

    return broadcast_item


def __get_or_create_broadcast(schedule, date):
    event = schedule.event

    try:
        broadcast = models.Broadcast.objects.get(schedule=schedule, date=date)
    except ObjectDoesNotExist:
        broadcast = models.Broadcast()
        broadcast.schedule = schedule
        broadcast.date = date

    if (not broadcast.get_video_embed_url()):
        if (schedule.youtube_channel):
            broadcast.video_youtube_channel = schedule.youtube_channel
        elif (event.youtube_channel):
            broadcast.video_youtube_channel = event.youtube_channel
        elif (schedule.video_url):
            broadcast.video_url = schedule.video_url
        elif (event.video_url):
            broadcast.video_url = event.video_url
        elif (event.location.youtube_channel):
            broadcast.video_youtube_channel = event.location.youtube_channel
        else:
            broadcast.video_url = event.location.video_url

        broadcast.video_iframe = __check_iframe_support(
            broadcast.get_video_embed_url())
        broadcast.save()

    if (not broadcast.text_url):
        text_url = None
        if (schedule.text_url):
            text_url = schedule.text_url
        elif (event.text_url):
            text_url = event.text_url
        else:
            try:
                liturgy_text = models.LiturgyText.objects.get(
                    liturgy=event.liturgy, date=date)
                if (liturgy_text):
                    text_url = liturgy_text.text_url
            except ObjectDoesNotExist:
                if (event.liturgy.text_url_pattern):
                    try:
                        text_url = date.strftime(
                            event.liturgy.text_url_pattern)
                    except ValueError:
                        pass

        if (text_url):
            broadcast.text_url = text_url
            broadcast.text_iframe = __check_iframe_support(text_url)
            broadcast.save()

    return broadcast


def __check_iframe_support(url):
    if (not url):
        return False

    try:
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        frame_header = response.getheader('X-Frame-Options')
        return frame_header is None
    except urllib.error.URLError:
        return True
        