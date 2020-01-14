from django.db import models
from django.utils import timezone
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    PASSWORD_HASH_PREFIX = 'pbkdf2_sha256'

    username = models.CharField(max_length=35, primary_key=True)
    name = models.CharField(max_length=35, null=True, blank=True, default=None)
    email = models.EmailField(unique=True)
    level = models.PositiveIntegerField(default=1)
    password_digest = models.CharField(max_length=65, default=None)  # PBKDF2 SHA256 Hash
    registred_date = models.DateTimeField(default=timezone.now)

    def __repr__(self):
        return f'User(username={repr(self.username)}, name={repr(self.name)}, ' \
               f'email={repr(self.email)}, level={repr(self.level)})'

    def set_password(self, new_password):
        if new_password:
            password_hash = make_password(new_password)
            self.password_digest = password_hash[len(User.PASSWORD_HASH_PREFIX):]
        else:
            self.password_digest = None

    def authenticate(self, password):
        return check_password(password, User.PASSWORD_HASH_PREFIX + self.password_digest)
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def create_user(username, email, password, name=None):
        user = User(username=username, name=name, email=email)
        user.set_password(password)
        user.save(force_insert=True)
        return user
