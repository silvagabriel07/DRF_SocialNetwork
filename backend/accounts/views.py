from rest_framework import generics, permissions, status
from rest_framework.views import Response, APIView
from accounts.models import User, Profile, Follow
from accounts.serializers import UserSerializer, ProfileSerializer, UserCreationSerializer, UserUpdateSerializer, MessageSerializer, FollowerSerializer, FollowedSerializer
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


class FollowUser(generics.CreateAPIView):
    def post(self, request, pk):
        request_profile = request.user.profile
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if request_profile.user.following.filter(followed=user).exists():
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        request_profile.follow(user)
        serializer = MessageSerializer({'message': 'You have successfully followed the user.'})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
            
follow_user_view = FollowUser.as_view()

class UnfollowUser(generics.DestroyAPIView):
    def delete(self, request, pk):
        request_profile = request.user.profile
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if not request_profile.user.following.filter(followed=user).exists():
            return Response({'detail': 'You were not following this user.'}, status=status.HTTP_400_BAD_REQUEST)

        request_profile.unfollow(user)
        serializer = MessageSerializer({'message': 'You have successfully unfollowed the user.'})
        return Response(serializer.data, status=status.HTTP_200_OK)
            
unfollow_user_view = UnfollowUser.as_view()


class FollowerList(generics.ListAPIView):
    serializer_class = FollowerSerializer
    queryset = Follow.objects.all()
    
    def get_queryset(self):
        user_followed_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(followed_id=user_followed_id)
         
follower_list_view = FollowerList.as_view()


class FollowedList(generics.ListAPIView):
    serializer_class = FollowedSerializer
    
    def get_queryset(self):
        user_follower_id = self.kwargs['pk']
        return Follow.objects.filter(follower_id=user_follower_id)
         
followed_list_view = FollowedList.as_view()
