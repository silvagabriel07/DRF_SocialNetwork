from rest_framework import serializers
from posts.models import Post, Tag, Comment, CommentLike, PostLike
from accounts.serializers import ProfileSimpleSerializer
from django.core.exceptions import ValidationError

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    # 'nested_tags' field is just to be see the tags and return them serialized 
    # 'tags' field expects a list of tag ids, and it's what we use as 'input'
    nested_tags = serializers.SerializerMethodField(read_only=True)
    author = ProfileSimpleSerializer(source='author.profile', required=False)
    
    def get_nested_tags(self, obj):
        ids = [tag.id for tag in obj.tags.all()]
        tags = Tag.objects.filter(id__in=ids)
        serializer = TagSerializer(tags, many=True)
        return serializer.data
        
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tags', 'nested_tags', 'created_at', 'total_likes', 'total_tags', 'total_comments',
        ]    
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'author': {'read_only': True, 'required': False},
            'tags': {'write_only': True, 'required': False}, 
            'nested_tags': {'read_only': True},
        }

    def validate_tags(self, values):
        if len(values) > 30:
            raise serializers.ValidationError({'detail': "A post can't have more than 30 tags."})
        return super().validate(values)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in tags:
                post.tags.add(tag)
        return post
    


class PostUpdateSerializer(PostSerializer):

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tags', 'nested_tags', 'created_at', 'total_likes', 'total_tags', 'total_comments',
        ]    
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'author': {'read_only': True, 'required': False},
            'nested_tags': {'read_only': True},
            'tags': {'write_only': True, 'required': False}, 
            'title': {'required': False},
            'content': {'required': False},
        }

    def validate_tags(self, values):
        if self.instance.tags.all().count() + len(values) > 30:
            raise serializers.ValidationError({'detail': "A post can't have more than 30 tags."})
        return super().validate(values)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        tags = validated_data.get('tags')
        if tags is not None:
            instance.tags.set(tags)
        try:
            instance.save()
        except ValidationError as e:
            raise serializers.ValidationError({'edited':{'detail': list(e)}}, code='invalid')
        return instance
    

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'author', 'created_at', 'total_likes']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'author': {'read_only': True},
            'post': {'required': False},
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        comment = Comment.objects.create(**validated_data)
        return comment
    
    
class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = '__all__'


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = '__all__'
        