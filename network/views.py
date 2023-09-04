import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q 
from django.http import HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Follow, Post, User, Like


def index(request):
    user = request.user
    if not request.user.is_authenticated:
        user = None
    all_posts = Post.objects.all().annotate(
        is_liked=Q(likes__user=user)
    )
    # TODO fix the is_liked invalid bug
    context = {
        "posts": all_posts
    }
    return render(request, "network/index.html", context)


@login_required
def all_posts(request):
    # do pagination
    posts = Post.objects.all()
    res = {"data": [post.serialize(request.user) for post in posts]}
    return JsonResponse(res)


@login_required
def following_posts(request):
    # do pagination
    posts = Post.objects.filter(author__in=request.user.following.values("following")).annotate(
        is_liked=Q(likes__user=request.user)
    )

    return render(request, "network/following.html", {"posts": posts})


def profile(request, username):
    posts = Post.objects.filter(author__username=username).annotate(
        is_liked=Q(likes__user=request.user)
    )
    
    return render(request, "network/profile.html", {
        "profile_user": User.objects.get(username=username),
        "posts": posts,
        "is_follower": Follow.objects.filter(
            follower=request.user,
            following__username=username
        ).exists(),
    })


@login_required
def create_post(request):
    content = request.POST.get("content")
    post = Post(content=content, author=request.user)
    post.save()

    return JsonResponse(post.serialize())


@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id)
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
