from random import choices

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class DistrictsNew(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    short_name = models.CharField(max_length=50, blank=True, null=True)
    division_name = models.CharField(max_length=50, blank=True, null=True)
    district_id = models.IntegerField(blank=True, null=True)
    division_id = models.IntegerField(blank=True, null=True)
    extent = models.CharField(max_length=100, blank=True, null=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'districts_new'


GENDER_CHOICES = (
    ('Boys', 'Boys'),
    ('Girls', 'Girls'),
)
LEVEL_CHOICES = (
    ('Primary', 'Primary'),
    ('Middle', 'Middle'),
    ('High School', 'High School'),
    ('High. Sec', 'High. Sec'),
)


# Create your models here.
class EecClubs(models.Model):
    emiscode = models.IntegerField(blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    head_name = models.CharField(max_length=255, blank=True, null=True)
    head_mobile_no_field = models.CharField(db_column='head_mobile_no  ', max_length=255, blank=True,
                                            null=True)  # Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.
    gender = models.CharField(max_length=255, blank=True, null=True, choices=GENDER_CHOICES)
    education_level = models.CharField(max_length=255, blank=True, null=True, choices=LEVEL_CHOICES)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    added_by = models.CharField(max_length=255, blank=True, null=True)
    district_id = models.ForeignKey(DistrictsNew, models.DO_NOTHING, verbose_name="District", db_column='district_id', blank=True, null=True)
    district_name = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    notification_path = models.FileField(upload_to='eec_notification', verbose_name="Notification", blank=True, null=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'eec_clubs'

    def save(self, *args, **kwargs):
        # Automatically update geom if latitude and longitude are not null
        if self.latitude is not None and self.longitude is not None:
            self.geom = Point(self.longitude, self.latitude, srid=4326)
        super(EecClubs, self).save(*args, **kwargs)
