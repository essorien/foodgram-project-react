from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        verbose_name='User Nickname',
        max_length=150,
        unique=True,
        validators=(RegexValidator(
            regex=r'^[\w.@+-]+\Z', message=(
                'Invalid value for "username" field.')
        ),)
    )
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=254,
        db_index=True,
        unique=True,
        help_text='Enter your email address',
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=150,
        help_text='Enter your first name',
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=150,
        help_text='Enter your last name',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Subscriber',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Author',
    )
    created = models.DateTimeField(
        'Subscription Date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
        )

    def __str__(self):
        return (f'User {self.user.username} '
                f'subscribed to {self.author.username}')
