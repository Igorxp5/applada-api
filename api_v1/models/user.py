from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    PASSWORD_HASH_PREFIX = 'pbkdf2_sha256'

    username = models.CharField(max_length=35, null=False, primary_key=True)
    name = models.CharField(max_length=35)
    email = models.EmailField(null=False, unique=True)
    level = models.PositiveIntegerField(default=1, null=False)
    password_digest = models.CharField(max_length=65, null=False, default=None)  # PBKDF2 SHA256 Hash
    registred_date = models.DateTimeField(auto_now_add=True)

    def set_password(self, new_password):
        password_hash = make_password(new_password)
        self.password_digest = password_hash[len(User.PASSWORD_HASH_PREFIX):]
    
    def authenticate(self, password):
        return check_password(password, User.PASSWORD_HASH_PREFIX + self.password_digest)

