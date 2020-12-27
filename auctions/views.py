from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils import timezone

from .models import User, Listing, Watch

import pytz

class NewListingForm(forms.Form):
   title = forms.CharField(label="Title")
   description = forms.CharField(label="Description")
   starting_bid = forms.FloatField(label="Starting bid")
   imageURL = forms.URLField(label="Image URL", required=False)
   category = forms.CharField(label="Category", required=False)

class WatchForm(forms.Form):
   listing_id = forms.IntegerField(widget=forms.HiddenInput ,label="listing_id")
   is_watched = forms.BooleanField(widget=forms.HiddenInput, label="is_watched", required=False)

def index(request):
   listings = Listing.objects.all()
   return render(request, "auctions/index.html", {
      "listings": listings
   })

def newListing(request):
   if request.method == "POST":
      form = NewListingForm(request.POST)

      if form.is_valid():
         listing = Listing(
            title=form.cleaned_data["title"],
            description=form.cleaned_data["description"],
            starting_bid=form.cleaned_data["starting_bid"],
            current_bid=form.cleaned_data["starting_bid"],
            imageURL=form.cleaned_data["imageURL"],
            category=form.cleaned_data["category"],
            created=timezone.now(),
            seller=User.objects.get(pk=request.user.id)
         )
         listing.save()
      else:
         print("invalid form")
      
      return HttpResponseRedirect(reverse("index"))


   form = NewListingForm()
   return render(request, "auctions/newListing.html", {
      "form": form
   })

def getListing(request, listing_id):
   listing = Listing.objects.get(pk=listing_id)
   ## check if the listing is being watched
   try:
      watch = Watch.objects.get(user=request.user, listings=listing)
      is_watched = True
   except Watch.DoesNotExist:
      is_watched = False

   form = WatchForm({
      "listing_id": listing_id,
      "is_watched": is_watched
   })

   return render(request, "auctions/listing.html", {
      "listing": listing,
      "seller": User.objects.get(pk=listing.seller.id),
      "form": form
   })

def watchListing(request):
   if request.method == "POST":
      form = WatchForm(request.POST)
      if form.is_valid():
         try:
            watch = Watch.objects.get(user=request.user)
         except Watch.DoesNotExist:
            watch = Watch(user=request.user)
            watch.save()
         listing_id = form.cleaned_data["listing_id"]

         listing = Listing.objects.get(pk=listing_id)
         if form.cleaned_data["is_watched"]:
            watch.listings.remove(listing)
         else:
            watch.listings.add(listing)

         return getListing(request, listing_id)
      print("invalid form")
      print(form.errors.as_json())

def myWatchList(request):
   watchlist = [item.listings for item in Watch.objects.filter(user=request.user)]
   return render(request, "auctions/myWatchList.html", {
      "watchlist": watchlist
   })


def login_view(request):
   if request.method == "POST":

      # Attempt to sign user in
      username = request.POST["username"]
      password = request.POST["password"]
      user = authenticate(request, username=username, password=password)

      # Check if authentication successful
      if user is not None:
         login(request, user)
         return HttpResponseRedirect(reverse("index"))
      else:
         return render(request, "auctions/login.html", {
               "message": "Invalid username and/or password."
         })
   else:
      return render(request, "auctions/login.html")


def logout_view(request):
   logout(request)
   return HttpResponseRedirect(reverse("index"))


def register(request):
   if request.method == "POST":
      username = request.POST["username"]
      email = request.POST["email"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
         return render(request, "auctions/register.html", {
               "message": "Passwords must match."
         })

      # Attempt to create new user
      try:
         user = User.objects.create_user(username, email, password)
         user.save()
      except IntegrityError:
         return render(request, "auctions/register.html", {
               "message": "Username already taken."
         })
      login(request, user)
      return HttpResponseRedirect(reverse("index"))
   else:
      return render(request, "auctions/register.html")
