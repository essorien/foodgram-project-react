from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from rest_framework.exceptions import ValidationError


class CustomUser(AbstractUser):
    """
    Custom User model.
    """
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        unique=True,
        validators=(RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=(
                'Invalid value entered for "Username" field.')
        ),)
    )
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        db_index=True,
        unique=True,
        help_text='Enter your email address.',
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=150,
        help_text='Enter your last name.',
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=150,
        help_text='Enter your first name.',
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('id',)

    def __str__(self):
        return f'{self.username}: {self.email}.'


class Subscription(models.Model):
    """
    Subscriber Model.
    """
    follower = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Follower',
    )
    followed_author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Followed Author',
    )
    subscription_date = models.DateTimeField(
        'Subscription Date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['follower', 'followed_author'],
                name='unique_following',
            ),
        )

    def clean(self):
        if self.follower == self.followed_author:
            raise ValidationError("You cannot subscribe to yourself.")

    def __str__(self):
        return (f'User {self.follower.username} '
                f'is following {self.followed_author.username}')
