from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Thread(models.Model):
    size = models.IntegerField(default=1)
    contacts = models.TextField(null=True)
    date = models.CharField(max_length=40, null=True)
    thread_id = models.TextField(null=True)


class UserProfile(models.Model):
    # reference to django's user model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=50)
    gmail_account = models.CharField(max_length=50, default='no email')
    friends = models.ManyToManyField("self", symmetrical=False, blank=True)
    contacts = models.TextField(null=True)
    threads = models.ManyToManyField(Thread, symmetrical=False, blank=True)
    bio = models.CharField(max_length=200, blank=True, default='')
    picture = models.CharField(blank=True, max_length=256)

    @staticmethod
    def get_user_profile_with_id(id):
        return UserProfile.objects.filter(user__exact=User.objects.filter(id__exact=id))[0]

