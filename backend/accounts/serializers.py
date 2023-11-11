from rest_framework import serializers
from accounts.models import User, Profile


class UserSerializer(serializers.ModelSerializer):
    profile_detail_url = serializers.HyperlinkedRelatedField(
        source='profile',
        many=False,
        read_only=True,
        view_name='profile-detail'
    )
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'is_active', 'profile_detail_url'
        ]

class ProfileSerializer(serializers.ModelSerializer):
    user_detail_url = serializers.HyperlinkedRelatedField(
        source='user',
        many=False,
        read_only=True,
        view_name='user-detail'
    )
    created_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%fZ", read_only=True)    

    class Meta:
        model = Profile
        fields = [
            'id', 'name', 'bio', 'created_at', 'picture', 'user_detail_url',           
        ]