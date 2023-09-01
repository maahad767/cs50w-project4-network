
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    # APIs
    path("posts/all", views.all_posts, name="all-posts"),  
    path("posts/my", views.my_posts, name="my-posts"),  
    path("posts/create", views.create_post, name="create-post"),  
      
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
