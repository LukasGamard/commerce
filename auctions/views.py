from django.contrib import admin
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import User, Listing, Bid, Comment

class NewListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        exclude = ["current_bid", "created", "seller", "highest_bidder", "active"]
        widgets = {
            "category": forms.Select,
            "description": forms.Textarea,
        }

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

class CloseBidForm(forms.Form):
    listing = forms.CharField(label="listing", required=True)

class NewCommentForm(forms.ModelForm):
    '''
    comment on a listing
    '''
    class Meta:
        model = Comment
        fields = "__all__"
        widgets = {
            "listing": forms.HiddenInput,
            "author": forms.HiddenInput,
            "datetime": forms.HiddenInput,
            "content": forms.Textarea,
        }

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })

@login_required
def newListing(request):
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["created"] = timezone.now()
        request.POST["seller"] = request.user
        form = NewListingForm(request.POST)

        if form.is_valid():
            form.save()
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

    if request.user.is_authenticated:
        watchform = WatchForm({
            "listing_id": listing.id,
            "is_watched": listing in request.user.watchlist.all()
        })
        bidform = BidForm({
            "user": request.user,
            "listing": listing
        })
        commentform = NewCommentForm({
            "author": request.user,
            "listing": listing
        })
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "seller": User.objects.get(pk=listing.seller.id),
            "watchform": watchform,
            "bidform": bidform,
            "commentform": commentform,
            "comments": Comment.objects.filter(listing=listing)
        })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "seller": User.objects.get(pk=listing.seller.id),
        "comments": Comment.objects.filter(listing=listing)
    })

def category(request, category_name=None):
    if category_name:
        # display the list of all listings in that category
        listings = Listing.objects.filter(category=category_name)
        return render(request, "auctions/category.html", {
            "category": category_name,
            "listings": listings
        })
    # display the list of all categories
    categories = [value.label for name, value in vars(Listing.Category).items() if name.isupper()]
    return render(request, "auctions/category.html", {
        "categories": categories
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

@login_required
def closeBid(request):
    if request.method == "POST":
        form = CloseBidForm(request.POST)
        
        if form.is_valid():
            listing = Listing.objects.get(title=form.cleaned_data["listing"])
            if request.user == listing.seller:
                listing.active = False
                listing.save()
 
        return getListing(request, listing.id)

@login_required
def newComment(request):
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["datetime"] = timezone.now()
        request.POST["author"] = request.user
        form = NewCommentForm(request.POST)

        if form.is_valid():
            form.save()
            listing = Listing.objects.get(title=form.cleaned_data["listing"])
            return getListing(request, listing.id)
        
        print("invalid form", form)



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
