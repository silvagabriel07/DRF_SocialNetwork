from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timezone
# Create your models here.

class User(AbstractUser):
    first_name = last_name = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'password', 'username']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(symmetrical=False)
    profile_name = models.CharField(max_length=20)
    bio = models.CharField(max_length=150)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='/profile_pictures/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, default=timezone.now())
            
    
    
