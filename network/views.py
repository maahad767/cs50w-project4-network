import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q 
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Post, User, Like


def index(request):
    all_posts = Post.objects.all().annotate(
        is_liked=Q(likes__user=request.user)
    )
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
    posts = Post.objects.filter(author=request.user)
    return render(request, "network/following.html", {"posts": posts})


def profile(request, username):
    posts = Post.objects.filter(author__username=username)
    
    return render(request, "network/profile.html")


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
