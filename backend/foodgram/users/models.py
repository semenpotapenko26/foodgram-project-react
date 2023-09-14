from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    '''Кастомная модель пользователя.'''
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Follow(models.Model):
    '''Модель для подписок.'''
    user = models.ForeignKey(
        CustomUser, related_name='follower', on_delete=models.CASCADE)
    author = models.ForeignKey(
        CustomUser, related_name='following', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]
