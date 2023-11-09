from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_save
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
    follow_from = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE) # who follow
    follow_to = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE) # who is followed
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.follow_from} follows {self.follow_to}"
    
    class Meta:
        unique_together = ('follow_from', 'follow_to')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # followers = models.ManyToManyField(User, symmetrical=False, related_name='following')
    profile_name = models.CharField(max_length=20)
    bio = models.CharField(max_length=150, blank=True, null=True)
    profile_picture = models.FileField(upload_to='profile_pictures/', default='/profile_pictures/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def follow(self, user):
        try:
            Follow.objects.create(
                follow_from=self.user,
                follow_to=user
            )
            return True
        except:
            return False
        
    def unfollow(self, user):
        try:
            follow = Follow.objects.get(
                follow_from=self.user,
                follow_to=user
            )
            follow.delete()
            return True
        except Follow.DoesNotExist:
            return False
    