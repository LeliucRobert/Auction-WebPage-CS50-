
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import Bid, Category, Listing, User, Comment

def listing(request , id):
    listingData = Listing.objects.get(pk=id)
   
    isListingInWatchList = request.user in listingData.watchlist.all()
    allComment = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username = listingData.owner.username

    return render(request , "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": isListingInWatchList,
        "allComments":allComment,
        "isOwner": isOwner
    })

def closeAuction(request , id):
    listingData = Listing.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    allComment = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username = listingData.owner.username

    return render(request , "auctions/listing.html", {
        "listing": listingData,
        "isListingInWatchlist": False,
        "allComments":allComment,
        "update": True,
        "message": "Auction closed successfully",
        "isOwner": isOwner

    })


def addComment(request , id):
    currentUser = request.user
    listingData = Listing.objects.get(pk=id)
    message = request.POST["newComment"]
    newComment = Comment(
        author=currentUser,
        listing=listingData,
        message=message
    )

    newComment.save()

    return HttpResponseRedirect(reverse("listing", args=(id,)))

def addBid(request , id):
    newBid = request.POST["newBid"]
    listingData = Listing.objects.get(pk=id)
    currentUser = request.user
    allComment = Comment.objects.filter(listing=listingData)
    isOwner = request.user.username = listingData.owner.username
    isListingInWatchList = request.user in listingData.watchlist.all()

    if float(newBid) > listingData.price.bid:
        updateBid = Bid(user=currentUser , bid=newBid)
        updateBid.save()
        listingData.price = updateBid
        listingData.save()
        
        return render(request , "auctions/listing.html", {
            "listing": listingData,
            "isListingInWatchlist": isListingInWatchList,
            "message": "Bid added successfully",
            "update": True,
            "allComments":allComment,
            "isOwner": isOwner

            })
    else:
        return render(request , "auctions/listing.html", {
            "listing": listingData,
            "message": "Bid must be greater than current bid",
            "update": False,
            "allComments":allComment,
            "isOwner": isOwner

            })
def watchList(request):
    currentUser = request.user
    listing = currentUser.watchlist.all()
    return render(request , "auctions/watchList.html" , {
        "listings": listing
    })

def removeWatchList(request , id):
    listingData = Listing.objects.get(pk=id)
    user = request.user
    listingData.watchlist.remove(user)
    return HttpResponseRedirect(reverse("listing", args=(id,)))

def addWatchList(request , id):
    listingData = Listing.objects.get(pk=id)
    user = request.user
    listingData.watchlist.add(user)
    return HttpResponseRedirect(reverse("listing", args=(id,)))

def index(request):
    activeListings = Listing.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "listings": activeListings,
        "categories": allCategories
    })

def createListing(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/createListing.html" , {
            "categories": allCategories
        })
    else:
       title= request.POST["title"]
       description = request.POST["description"] 
       imageUrl = request.POST["imageUrl"]
       price = request.POST["price"]
       category = request.POST["category"]
       owner = request.user

       categoryData = Category.objects.get(categoryName=category)
       
       bid = Bid(bid= float(price) , user=owner)
       bid.save()

       newListing = Listing(title=title,
                            description=description,
                            imageUrl=imageUrl,
                            price=bid,
                            category=categoryData,
                            owner=owner)
       newListing.save()

       return HttpResponseRedirect(reverse("index"))
    
def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryForm)
        activeListings = Listing.objects.filter(isActive=True , category=category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html", {
            "listings": activeListings,
            "categories": allCategories
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
