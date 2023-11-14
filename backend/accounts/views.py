from rest_framework import generics, permissions
from accounts.models import User, Profile
from accounts.serializers import UserSerializer, ProfileSerializer, UserCreationSerializer
# Create your views here.

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
user_detail_view = UserDetail.as_view()


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
user_list_view = UserList.as_view()


class UserRegistration(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = [permissions.AllowAny]
    
user_registration_view = UserRegistration.as_view()



class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
profile_detail_view = ProfileDetail.as_view()

