import django.contrib.auth.models
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.urls import reverse


class Doctor(models.Model):
    CHOICE_SEX = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    doctor_user = models.OneToOneField(User, on_delete=models.CASCADE)
    experience = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to="media/doctor_images", blank=True)
    first_name = models.CharField(max_length=200, default='')
    last_name = models.CharField(max_length=200, default='')
    phoneNum = models.CharField(max_length=50, default='')
    slug = models.SlugField(default=first_name.__str__()+'_'+last_name.__str__())
    sex = models.CharField(max_length=100, choices=CHOICE_SEX, default='')


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    money = models.TextField()

    @staticmethod
    def get_purse_by_userid(user_id):
        return Wallet.objects.filter(user_id=user_id).first()

