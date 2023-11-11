from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
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

    
@receiver(pre_save, sender=Follow)
def check_self_following(sender, instance, **kwargs):
    if instance.follower == instance.followed:
        raise ValidationError('You can not follow yourself')    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_name = models.CharField(max_length=20, null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    profile_picture = models.FileField(upload_to='profile_pictures/', default='/profile_pictures/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def follow(self, user):
        try:
            Follow.objects.create(
                follower=self.user,
                followed=user
            )
            return True
        except:
            return False
        
    def unfollow(self, user):
        try:
            follow = Follow.objects.get(
                follower=self.user,
                followed=user
            )
            follow.delete()
            return True
        except Follow.DoesNotExist:
            return False
        
    @property
    def followers(self):
        return self.user.followers.all()
    
    @property
    def following(self):
        return self.user.following.all()


@receiver(post_save, sender=User)
def signup_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )