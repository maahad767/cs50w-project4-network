import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Case, When, BooleanField, Value
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Follow, Post, User, Like


def index(request):
    user = request.user
    if not request.user.is_authenticated:
        user = None
    all_posts = [post.serialize(user) for post in Post.objects.all()]

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # TODO fix the is_liked invalid bug
    context = {
        "page_obj": page_obj
     }
    return render(request, "network/index.html", context)


@login_required
def following_posts(request):
    user = request.user
    if not request.user.is_authenticated:
        user = None
    posts = [post.serialize(user) for post in Post.objects.filter(author__in=request.user.following.values("following"))]
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number) 
    context = {
        "page_obj": page_obj
     }

    return render(request, "network/following.html", context)


def profile(request, username):
    user = request.user
    if not user.is_authenticated:
        user = None
    posts = [post.serialize(user) for post in Post.objects.filter(author__username=username)]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "network/profile.html", {
        "profile_user": User.objects.get(username=username),
        "page_obj": page_obj,
        "is_follower": Follow.objects.filter(
            follower=user,
            following__username=username
        ).exists(),
    })


@login_required
def create_post(request):
    content = request.POST.get("content")
    post = Post(content=content, author=request.user)
    post.save()

    return redirect(reverse("index")) 


@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id, author=request.user)
    post.content = json.loads(request.body)["content"]
    post.save()
    return JsonResponse(post.serialize())

@login_required
def like_post(request, post_id):
    Like.objects.get_or_create(
        user=request.user,
        post_id=post_id,
    )
    data = {
        "like_count": Post.objects.get(id=post_id).likes.count(),
    }
    return JsonResponse(data)


@login_required
def unlike_post(request, post_id):
    like = Like.objects.get(
        user=request.user,
        post_id=post_id,
    )
    like.delete()
    data = {
        "like_count": Post.objects.get(id=post_id).likes.count(),
    }
    return JsonResponse(data)

@login_required
def follow(request, username):
    follow_user = User.objects.get(username=username)
    Follow.objects.get_or_create(
        follower=request.user,
        following=follow_user,
    )
    
    return JsonResponse({"follower_count": follow_user.followers.count()})


@login_required
def unfollow(request, username):
    unfollow_user = User.objects.get(username=username)
    try:
        follow_obj = Follow.objects.get(
            follower=request.user,
            following=unfollow_user,
        )
        follow_obj.delete()
    except:
        print("Not Followed")
        return HttpResponseBadRequest("Not Followed")
    return JsonResponse({"follower_count": unfollow_user.followers.count()})

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
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


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
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
