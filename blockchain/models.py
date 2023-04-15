import datetime

from django.db import models


class Block(models.Model):
    timestamp = models.TextField(default=datetime.date.today())
    transactions = models.TextField('Transactions')
    proof = models.IntegerField()
    previous_hash = models.TextField('Hash')


