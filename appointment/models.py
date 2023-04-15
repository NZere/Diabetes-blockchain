from django.db import models
from django.utils import timezone

from market.models import Product
from users.models import Doctor
from django.contrib.auth.models import User


class All_work_times(models.Model):
    date = models.DateTimeField()
    time = models.TimeField()


class Schedule(models.Model):
    CHOICE_STATUS = (
        ('0', 'open'),
        ('1', 'done'),
        ('2', 'not-yet')
    )
    work_time = models.ForeignKey(All_work_times, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=CHOICE_STATUS, default='')
    info = models.CharField(max_length=100)


class Recommendation_product(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

