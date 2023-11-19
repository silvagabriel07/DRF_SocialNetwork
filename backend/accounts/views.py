from rest_framework import generics, permissions, status
from rest_framework.views import Response, APIView
from accounts.models import User, Profile
from accounts.serializers import UserSerializer, ProfileSerializer, UserCreationSerializer, UserUpdateSerializer
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


class UserUpdate(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        if not request.user == user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        return super().update(request, *args, **kwargs)

user_update_view = UserUpdate.as_view()    


class UserDelete(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        if not request.user == user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)

user_delete_view = UserDelete.as_view()    


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
profile_detail_view = ProfileDetail.as_view()


class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
profile_list_view = ProfileList.as_view()


class ProfileUpdate(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        if not request.user == profile.user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, *args, **kwargs)
    
profile_update_view = ProfileUpdate.as_view()


