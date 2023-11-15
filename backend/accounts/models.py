from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from posts.models import Post, PostLike, Comment, CommentLike
# Create your models here.

class User(AbstractUser):
    first_name = last_name = None
    username = models.CharField(max_length=60, unique=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self) -> str:
        return self.username

    # methods related to authorizathion and permissions


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE) # who follow
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE) # who is followed
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.follower} follows {self.followed}"
    
    def clean(self):
        if self.followed == self.follower:
            raise ValidationError('User cannot follow themselves.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('follower', 'followed')

    
@receiver(pre_save, sender=Follow)
def check_self_following(sender, instance, **kwargs):
    if instance.follower == instance.followed:
        raise ValidationError('You can not follow yourself')    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, null=True, blank=True)
    bio = models.CharField(max_length=150, null=True, blank=True)
    picture = models.FileField(upload_to='profile_pictures/', default='/profile_pictures/default_profile_picture.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f'{self.name} {self.id}'
    
    # methods related to social network logic

    def like_post(self, post):
        try:
            PostLike.objects.create(user=self.user, post=post)
        except IntegrityError:
            raise ValidationError("You have already liked this post.")
            
    def follow(self, user):
        try:
            Follow.objects.create(follower=self.user, followed=user)
        except IntegrityError:
            raise ValidationError("You are already following this user.")
    
    def unfollow(self, user):
        try:
            follow = Follow.objects.get(follower=self.user, followed=user)
            follow.delete()
        except Follow.DoesNotExist:
            raise ValidationError("You are not following this user.")
    
    @property
    def total_followers(self):
        return self.user.followers.all().count()
    
    @property
    def total_following(self):
        return self.user.following.all().count()
    

@receiver(post_save, sender=User)
def signup_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )


