from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newListing", views.newListing, name="newListing"),
    path("auction/<str:listing_id>", views.getListing, name="listing"),
    path("watchListing", views.watchListing, name="watchListing"),
    path("myWatchList", views.myWatchList, name="myWatchList")
]
