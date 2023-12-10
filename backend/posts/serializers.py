from typing import List
from rest_framework import serializers
from posts.models import Post, Tag, Comment, CommentLike, PostLike
from accounts.serializers import ProfileSimpleSerializer
from posts.mixins import PostValidationMixin, PostSerializerMixin

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class PostSerializer(PostValidationMixin, PostSerializerMixin, serializers.ModelSerializer):        
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tags', 'nested_tags', 'created_at', 'total_likes', 'total_tags', 'total_comments', 'edited'
        ]    
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'author': {'read_only': True, 'required': False},
            'tags': {'write_only': True, 'required': False}, 
            'nested_tags': {'read_only': True},
            'edited': {'read_only': True},
        }
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['author'] = request.user
        tags = validated_data.pop('tags')
        post = Post.objects.create(**validated_data)
        for tag in tags:
                post.tags.add(tag)
        return post
    

class PostUpdateSerializer(PostValidationMixin, PostSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tags', 'nested_tags', 'created_at', 'total_likes', 'total_tags', 'total_comments', 'edited'
        ]    
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'author': {'read_only': True, 'required': False},
            'nested_tags': {'read_only': True},
            'tags': {'write_only': True, 'required': False}, 
            'title': {'required': False},
            'content': {'required': False},
            'edited': {'read_only': True},
        }

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.edited = validated_data.get('edited', instance.edited)
        tags = validated_data.get('tags')
        if tags is not None:
            instance.tags.set(tags)
        instance.save()
        return instance


class PostDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'author', 'tags', 'created_at', 'total_likes', 'total_tags', 'total_comments', 'edited'
        ]    


class CommentSerializer(serializers.ModelSerializer):
    author = ProfileSimpleSerializer(source='author.profile', required=False)
    
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
    profile = ProfileSimpleSerializer(source='user.profile', required=False)

    class Meta:
        model = CommentLike
        fields = ['id', 'profile', 'comment', 'created_at']


class PostLikeSerializer(serializers.ModelSerializer):
    profile = ProfileSimpleSerializer(source='user.profile', required=False)
                                     
    class Meta:
        model = PostLike
        fields = ['id', 'profile', 'post', 'created_at']
        