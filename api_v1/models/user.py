from django.db import models
from django.utils import timezone
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password


class User(AbstractUser):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    first_name = models.CharField(_('name'), max_length=30, 
                                  blank=True, null=True, default=None)
    email = models.EmailField(_('email'), unique=True)
    level = models.PositiveIntegerField(default=1)

    def __repr__(self):
        return f'User(username={repr(self.username)}, name={repr(self.first_name)}, ' \
               f'email={repr(self.email)}, level={repr(self.level)})'
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
