from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import User, Listing, Bid

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description")
    starting_bid = forms.FloatField(label="Starting bid")
    imageURL = forms.URLField(label="Image URL", required=False)
    category = forms.CharField(label="Category", required=False)

class WatchForm(forms.Form):
    listing_id = forms.IntegerField(widget=forms.HiddenInput ,label="listing_id")
    is_watched = forms.BooleanField(widget=forms.HiddenInput, label="is_watched", required=False)

class BidForm(forms.ModelForm):
    '''
    form based on the Bid model
    '''
    class Meta:
        model = Bid
        fields = "__all__"
        widgets = {
            "user": forms.HiddenInput,
            "listing": forms.HiddenInput,
        }

    def clean(self):
        cleaned_data = super().clean()
        listing = cleaned_data.get("listing")
        amount = cleaned_data.get("amount")

        # If fields are correct
        if listing and amount:
            if listing.current_bid:
                current = listing.current_bid
            else:
                current = listing.starting_bid
            if amount <= current:
                raise ValidationError(
                    "Your bid must be higher than the current bid."
                )

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })

@login_required
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

    watchform = WatchForm({
        "listing_id": listing.id,
        "is_watched": listing in request.user.watchlist.all()
    })
    bidform = BidForm({
        "user": request.user,
        "listing": listing
    })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "seller": User.objects.get(pk=listing.seller.id),
        "watchform": watchform,
        "bidform": bidform
    })

@login_required
def watchListing(request):
    if request.method == "POST":
        form = WatchForm(request.POST)
        if form.is_valid():
            # Get the Listing
            listing_id = form.cleaned_data["listing_id"]
            listing = Listing.objects.get(pk=listing_id)
            # Get the User
            user = request.user
            if form.cleaned_data["is_watched"]:
                user.watchlist.remove(listing)
            else:
                user.watchlist.add(listing)

            return getListing(request, listing_id)

@login_required
def bid(request):
    '''
    create a new Bid instance for the current User and Listing
    '''
    if request.method == "POST":
        bidform = BidForm(request.POST)
        if bidform.is_valid():
            # Create a new Bid from the form
            newBid = bidform.save()
            # make User highest_bid of the Listing
            listing = newBid.listing
            listing.current_bid = bidform.cleaned_data["amount"]
            listing.highest_bidder = request.user
            listing.save()
            return getListing(request, listing.id)

        listing = Listing.objects.get(id=bidform.data["listing"])
        watchform = WatchForm({
            "listing_id": listing.id,
            "is_watched": listing in request.user.watchlist.all()
        })

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "seller": User.objects.get(pk=listing.seller.id),
            "watchform": watchform,
            "bidform": bidform
        })   

@login_required
def myWatchList(request):
    watchlist = request.user.watchlist.all()
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


@login_required
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
