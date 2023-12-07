from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.utils import IntegrityError
from posts.models import PostLike, CommentLike
from django.core.exceptions import ValidationError

# Create your models here.

class User(AbstractUser):
    first_name = last_name = None
    username = models.CharField(max_length=60, unique=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE) # who follow
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE) # who is followed
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.follower} follows {self.followed}"

    class Meta:
        unique_together = ('follower', 'followed')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    picture = models.FileField(upload_to='profile_pictures/', default='/profile_pictures/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f'{self.name} {self.id}'
    
    @property
    def total_followers(self) -> int:
        return self.user.followers.all().count()
    
    @property
    def total_following(self) -> int:
        return self.user.following.all().count()
    
    @property
    def total_posts(self) -> int:
        return self.user.posts.all().count()
