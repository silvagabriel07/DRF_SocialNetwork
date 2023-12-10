from accounts.serializers import ProfileSimpleSerializer
from rest_framework import serializers
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from typing import List


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


class PostSerializerMixin(serializers.ModelSerializer):
    # 'nested_tags' field is just to be see the tags and return them serialized 
    # 'tags' field expects a list of tag ids, and it's what we use as 'input'
    author = ProfileSimpleSerializer(source='author.profile', required=False)
    nested_tags = serializers.SerializerMethodField(read_only=True)
    
    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_nested_tags(self, obj) -> List[str]:
        from posts.serializers import TagSerializer
        tags = obj.tags.all()
        serializer = TagSerializer(tags, many=True)
        return serializer.data
    
    