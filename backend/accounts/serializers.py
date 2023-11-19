from rest_framework import serializers
from accounts.models import User, Profile, Follow
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class UserSerializer(serializers.ModelSerializer):
    profile_detail_url = serializers.HyperlinkedRelatedField(
        source='profile',
        many=False,
        read_only=True,
        view_name='profile-detail'
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'is_active', 'profile_detail_url'
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'read_only': True,},
        }
    

class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_active']
        extra_kwargs = {
            'id': {'read_only': True},
            'is_active': {'read_only': True,},
            'password': {'write_only':True}
            }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
            )
        return user
    
    def validate_password(self, value):
        user = User(
            username='username',
            email='email',
            password=value
            )
        try:
            validators.validate_password(password=value, user=user)
        except ValidationError as err:
            raise serializers.ValidationError(err.messages)
        return value


class UserUpdateSerializer(UserCreationSerializer):
    old_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'old_password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            }
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', instance.password)
        instance.set_password(password)
        instance.save()
        return instance
    
    def validate(self, data):
        user = self.instance
        old_password = data.get('old_password')
        
        if not check_password(old_password, user.password):
            raise serializers.ValidationError({'old_password': 'Incorrect old password.'})
        
        return data

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)    

    class Meta:
        model = Profile
        fields = [
            'id', 'name', 'bio', 'created_at', 'picture', 'user', 'total_posts', 'total_followers', 'total_following'        
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'created_at': {'read_only': True},
        }
        
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.bio = validated_data.get('bio',instance.bio)
        
        instance.picture = validated_data.get('picture', instance.picture)
        instance.save()
        return instance


class FollowUserSerializer(serializers.Serializer):
    message = serializers.CharField()


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='follower')    
    class Meta:
        model = Follow
        fields = ['user', 'created_at']


class FollowedSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='followed')    
    class Meta:
        model = Follow
        fields = ['user', 'created_at']
