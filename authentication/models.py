import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class FlightUser(AbstractUser):
    email = models.EmailField('email address', blank=True, unique=True)
    first_name = models.CharField('first name', max_length=30, blank=False)
    last_name = models.CharField('last name', max_length=150, blank=False)

    username = models.CharField(
        'username',
        max_length=150,
        unique=False,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def token(self):
        """
        Generates the token and allows the token
        to be called by `user.token`
        :return string
        """
        token = jwt.encode(
            {
                "id": self.id,
                "username": self.username,
                "email": self.email,
            },
            settings.SECRET_KEY, algorithm='HS256').decode()
        return token
