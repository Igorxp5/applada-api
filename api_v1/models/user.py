from django.db import models
from django.utils import timezone
from django.db.utils import IntegrityError
from django.utils.translation import gettext as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password

from api_v1.translation import error_messages as e_

class User(AbstractUser):
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser.username_validator],
        error_messages=e_('Username'),
    )
    email = models.EmailField(_('Email'), unique=True, error_messages=e_('Email'))
    level = models.PositiveIntegerField(default=1)
    password = models.CharField(_('password'), max_length=128, error_messages=e_('Password'))

    def __repr__(self):
        return f'User(username={repr(self.username)}, name={repr(self.name)}, ' \
               f'email={repr(self.email)}, level={repr(self.level)})'
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
