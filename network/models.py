from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def serialize(self):
        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }
    
    
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    
    created_at = models.DateTimeField(auto_now_add=True)
    

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.id}: {self.title}"

    def serialize(self):
        return {
            "id": self.pk,
            "content": self.content,
            "author": self.author.serialize(),
            "created_at": self.created_at.strftime("%B %d, %Y, %I:%M %p"),
            "likes": self.likes.count()
        }

    class Meta:
        ordering = ["-created_at"]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    