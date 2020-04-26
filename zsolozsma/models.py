from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify


class Location(models.Model):
    """Helyszín"""

    name = models.CharField('Rövid név', max_length=100, blank=False)
    fullname = models.CharField(
        'Teljes név', max_length=300, blank=False, unique=True)
    slug = models.SlugField('URL részlet', max_length=50,
                            blank=False, unique=True)
    homepage = models.URLField('Honlap', blank=True)
    youtube_channel = models.CharField(
        'YouTube csatorna ID', max_length=20, blank=True)
    video_url = models.URLField(
        'URL a közvetítéshez', max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return "%s (%s)" % (self.name, self.fullname)


class Liturgy(models.Model):
    """Szertartás"""

    name = models.CharField('Név', max_length=100, blank=False, unique=True)
    description = models.TextField('Leírás', max_length=500, blank=True)
    slug = models.SlugField('URL részlet', max_length=50,
                            blank=False, unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Liturgy, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    """Közvetített esemény (adott szertartás egy adott helyen, adott időpontban)"""

    class Weekdays(models.IntegerChoices):
        hétfő = 0,
        kedd = 1,
        szerda = 2,
        csütörtök = 3,
        péntek = 4,
        szombat = 5,
        vasárnap = 6

    location = models.ForeignKey(
        "Location", verbose_name='Helyszín', on_delete=models.CASCADE, blank=False)
    liturgy = models.ForeignKey(
        "Liturgy", verbose_name='Szertartás', on_delete=models.CASCADE, blank=False)
    name = models.CharField('Név', max_length=100, blank=False)
    slug = models.SlugField('URL részlet', max_length=100, blank=False)

    day_of_week = models.IntegerField(
        'Hét napja', null=True, blank=True, choices=Weekdays.choices)
    time = models.TimeField('Kezdés ideje', auto_now=False,
                            auto_now_add=False, null=True, blank=True)
    video_url = models.URLField(
        'Egyedi URL a közvetítéshez', max_length=500, blank=True)
    text_url = models.URLField('Egyedi szöveg URL', max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        date_str = Event.Weekdays(self.day_of_week).name

        return "%s (%s %s %s %s)" % (self.name, self.location.name, self.liturgy.name, date_str, self.time)


class LiturgyText(models.Model):
    """Egy szertartás szövegei"""

    liturgy = models.ForeignKey(
        "Liturgy", verbose_name="Szertartás", on_delete=models.CASCADE, blank=False)
    date = models.DateField("Dátum", auto_now=False,
                            auto_now_add=False, blank=False)
    text_url = models.URLField('Szöveg URL', max_length=500, blank=True)
