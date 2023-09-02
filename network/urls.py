
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    # APIs
    path("posts/all", views.all_posts, name="all-posts"),  
    path("posts/following", views.following_posts, name="following-posts"),  
    path("posts/create", views.create_post, name="create-post"),  
    path("profile/<str:username>", views.profile, name="profile"),  
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
