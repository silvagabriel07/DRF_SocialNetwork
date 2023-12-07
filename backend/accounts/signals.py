from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from accounts.models import Profile, User, Follow
from django.core.exceptions import ValidationError

@receiver(post_save, sender=User)
def signup_create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )

@receiver(pre_save, sender=Follow)
def check_self_following(sender, instance, **kwargs):
    if instance.follower == instance.followed:
       raise ValidationError("You can not follow yourself.")
   