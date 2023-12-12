from posts.models import Post
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

@receiver(m2m_changed, sender=Post.tags.through)
def limit_tags(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if instance.tags.count() + len(pk_set) > 30:
            raise ValidationError("A post can't have more than 30 tags.")

