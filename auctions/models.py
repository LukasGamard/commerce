from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass

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
   )

   def __str__(self):
      return f"{self.title}"

class Bid(models.Model):
   amount = models.IntegerField()
   user_id = models.ForeignKey(
      'User',
      on_delete=models.CASCADE,
   )
   listing_id = models.ForeignKey(
      'Listing',
      on_delete=models.CASCADE,
   )

class Comment(models.Model):
   text = models.CharField(max_length=300)
   created = models.DateTimeField()
   listing_id = models.ForeignKey(
      'Listing',
      on_delete=models.CASCADE,
   )
   user_id = models.ForeignKey(
      'User',
      on_delete=models.CASCADE,
   )

class Watch(models.Model):
   user = models.ForeignKey(
      "User",
      on_delete=models.CASCADE,
   )
   listings = models.ManyToManyField(Listing)