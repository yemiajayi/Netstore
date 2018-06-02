from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Auction(models.Model):
    title = models.CharField(max_length=50)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    winner = models.CharField(max_length=100, null=True)
    description = models.TextField(max_length=1000)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Starting price", default=1.00)
    deadline = models.DateTimeField(help_text="format: YYYY-MM-DD HH:MM", default=timezone.now()+timedelta(hours=72))
    version = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    banned = models.BooleanField(default=False)
    due = models.BooleanField(default=False)
    adjudicated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['deadline']


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, help_text="raise bid with this amount")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-bid']