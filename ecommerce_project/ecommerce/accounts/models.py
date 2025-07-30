# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.contrib.auth.models import AbstractUser

# class CustomUser(AbstractUser):
#     first_name = models.CharField(max_length=30, blank=True)  # The problematic field
#     last_name = models.CharField(max_length=30, blank=True)
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='customuser_set',
#         blank=True,
#         help_text='The groups this user belongs to.',
#         verbose_name='groups',
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='customuser_set',
#         blank=True,
#         help_text='Specific permissions for this user.',
#         verbose_name='user permissions',
#     )

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # The fields first_name, last_name, groups, and user_permissions
    # are inherited from AbstractUser, so they are removed from here to avoid conflicts.

    # This is the new field to define the user's role.
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('User', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')

    def __str__(self):
        return self.username