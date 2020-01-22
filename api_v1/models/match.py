from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point

from rest_framework.exceptions import ValidationError

from enum import Enum
from datetime import timedelta

from . import User


class MatchCategory(Enum):
    SOCCER = ('soccer', _('Soccer'))
    VOLEYBALL = ('volleyball', _('Voleyball'))
    BASKETBALL = ('basketball', _('Basketball'))
    
    def __str__(self):
        return self.value[0]

    @staticmethod
    def choices():
        return [category.value for category in MatchCategory]


class MatchStatus(Enum):
    ON_HOLD = 'on_hold', lambda now, duration: dict(date__lt=now)
    ON_GOING = 'on_going', lambda now, duration: dict(date__range=(now, now + duration))
    FINISHED = 'finished', lambda now, duration: dict(date__gte=now)

    def __new__(cls, value, queryset_filter):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.queryset_filter = queryset_filter
        return obj

    def __str__(self):
        return str(self.value)
    
    def get_queryset_filter(self):
        return self.queryset_filter(timezone.now())

    @staticmethod
    def get_match_status(match):
        today = timezone.now()
        if today < match.date:
            return MatchStatus.ON_HOLD
        elif today >= match.date and today < match.date + match.duration:
            return MatchStatus.ON_GOING
        return MatchStatus.FINISHED



class Match(gis_models.Model):
    title = gis_models.CharField(_('title'), max_length=50)
    description = gis_models.CharField(_('description'), max_length=255, null=True, blank=True)
    limit_participants = gis_models.PositiveIntegerField(_('limit participants'), null=True, blank=True)
    owner = gis_models.ForeignKey(User, on_delete=gis_models.CASCADE)
    duration = gis_models.DurationField(_('duration'))
    location = gis_models.PointField(_('location'))
    date = gis_models.DateTimeField(_('date'))
    category = gis_models.CharField(_('category'), max_length=15, default=None, 
                                choices=MatchCategory.choices())
    updated_date = gis_models.DateTimeField(auto_now=True)
    created_date = gis_models.DateTimeField(auto_now_add=True)

    @property
    def latitude(self):
        return self.location.y
    
    @property
    def longitude(self):
        return self.location.x
    
    def clean(self):
        if self.limit_participants:
            subscriptions = MatchSubscription.objects.filter(match=self.id)
            if self.limit_participants < len(subscriptions):
                raise ValidationError(_('Limit participants must be grater '
                                        'than current total participants'))
        if self.date and self.date < timezone.now():
            raise ValidationError(_('Match date cannot be in the past'))
        
        if self.date and self.date < (timezone.now() + timedelta(hours=1)):
            raise ValidationError(_('Match date must be at least one hour longer than now'))
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @staticmethod
    @receiver(post_save, sender='api_v1.Match')
    def post_save(created, instance, **kwargs):
        # Create owner's match subscription always a match is created
        if created:
            MatchSubscription.objects.create(match=instance, user=instance.owner)


class MatchSubscription(models.Model):
    class Meta:
        unique_together = (('match', 'user'),)

    match = models.ForeignKey(Match, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)


class MatchChatMessage(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    message = models.TextField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
