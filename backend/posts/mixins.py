from rest_framework import serializers
from django.utils import timezone


class PostValidationMixin:
    def validate_tags(self, value):
        max_tags_allowed = 30
        if self.instance:
            current_tags_count = self.instance.tags.all().count()
            if current_tags_count + len(value) > max_tags_allowed:
                raise serializers.ValidationError({'detail': f"A post can't have more than {max_tags_allowed} tags."})
        else:
            if len(value) > max_tags_allowed:
                raise serializers.ValidationError({'detail': f"A post can't have more than {max_tags_allowed} tags."})
        return value

    def validate_edited(self, instance):
        if instance.edited:
            raise serializers.ValidationError({'detail': 'This post has already been edited.'})

    def validate_editable_time(self, instance):
        max_editable_time = timezone.timedelta(hours=12)
        if timezone.now() > instance.created_at + max_editable_time:
            raise serializers.ValidationError({"detail": "This post cannot be edited any further."})

    def validate(self, attrs):
        if self.instance:
            self.validate_edited(self.instance)
            self.validate_editable_time(self.instance)
            self.instance.edited = True
        return super().validate(attrs)