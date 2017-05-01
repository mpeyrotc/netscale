from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    # reference to django's user model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    gmail_account = models.CharField(max_length=50, default='no email')
    friends = models.ManyToManyField("self", symmetrical=False, blank=True)
    contacts = models.TextField(null=True)

    @staticmethod
    def get_user_profile_with_id(id):
        return UserProfile.objects.filter(user__exact=User.objects.filter(id__exact=id))[0]

