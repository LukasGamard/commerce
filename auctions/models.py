'''
models for auction
'''

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class Listing(models.Model):

    class Category(models.TextChoices):
        TOY = "TO", _("Toys")
        FASHION = "FA", _("Fashion")
        ELECTRONICS = "EL", _("Electronics")
        HOME = "HO", _("Home")
        OTHERS = "OT", _("Others")

    title = models.CharField(max_length=64)
    description = models.CharField(max_length=300)
    starting_bid = models.FloatField()
    current_bid = models.FloatField(null=True)
    imageURL = models.URLField(null=True)
    category = models.CharField(
        max_length=2,
        choices=Category.choices,
        null=True,
    )
    created = models.DateTimeField()
    seller = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="seller",
    )
    highest_bidder = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="highest_bid",
        null=True,
    )

    def __str__(self):
        return f"{self.title}"

class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing)

class Bid(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
    )

class Comment(models.Model):
    text = models.CharField(max_length=300)
    created = models.DateTimeField()
    listing = models.ForeignKey(
        'Listing',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
    )