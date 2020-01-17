from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from enum import Enum

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
    
class Match(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    limit_participants = models.PositiveIntegerField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(_('Date'))
    category = models.CharField(max_length=15, default=None, 
                                choices=MatchCategory.choices())
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        limit_participants = self.limit_participants
        if limit_participants:
            subscriptions = MatchSubscription.objects.filter(match=self.id)
            if limit_participants < len(subscriptions):
                raise ValidationError(message=_('Limit participants must be grater '
                                                'than current total participants'))
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @receiver(post_save, sender='api_v1.Match')
    def post_save(created, instance, **kwargs):
        # Create owner's match subscription always a match is created
        if created:
            MatchSubscription(match=instance, user=instance.owner).save()


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
