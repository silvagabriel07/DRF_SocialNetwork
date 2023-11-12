from rest_framework import generics, permissions
from accounts.models import User, Profile
from accounts.serializers import UserSerializer, ProfileSerializer
# Create your views here.

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
user_detail_view = UserDetail.as_view()


class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
user_list_create_view = UserListCreate.as_view()


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
profile_detail_view = ProfileDetail.as_view()

