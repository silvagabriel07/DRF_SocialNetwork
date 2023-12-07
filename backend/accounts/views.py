from rest_framework import generics, permissions, status, serializers
from rest_framework.views import Response
from accounts.models import User, Profile, Follow
from accounts.serializers import (
    UserSerializer, ProfileSerializer, UserCreationSerializer, UserUpdateSerializer,
    MessageSerializer, FollowerSerializer, FollowedSerializer
)
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.filters import UserFilter, ProfileFilter, FollowerFilter, FollowedFilter
from drf_spectacular.utils import extend_schema
# Create your views here.

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
user_detail_view = UserDetailView.as_view()


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    
user_list_view = UserListView.as_view()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserCreationSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)

user_registration_view = UserRegistrationView.as_view()


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        if not request.user == user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        return super().update(request, *args, **kwargs)

user_update_view = UserUpdateView.as_view()    


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        if not request.user == user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)

user_delete_view = UserDeleteView.as_view()    


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
profile_detail_view = ProfileDetailView.as_view()


class ProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filterset_class = ProfileFilter

profile_list_view = ProfileListView.as_view()


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        if not request.user == profile.user:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        return super().update(request, *args, **kwargs)
    
profile_update_view = ProfileUpdateView.as_view()


@extend_schema(
    summary="Follow a User",
    description="Endpoint for follow a specific user.",
    responses={
        201: MessageSerializer,
        404: {"detail": "The user does not exist."},
        400: {"detail": "You are already following this user."}
        },
)
class FollowUserView(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def post(self, request, pk):
        request_user = request.user
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if request_user.following.filter(followed=user).exists():
            return Response({'detail': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        elif request_user.id == user.id:
            return Response({'detail': 'You can not follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        else:            
            Follow.objects.create(follower=request_user, followed=user)
            serializer = MessageSerializer({'message': 'You have successfully followed the user.'})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
follow_user_view = FollowUserView.as_view()


@extend_schema(
    summary="Unfollow a User",
    description="Endpoint for unfollow a specific user.",
    responses={
        200: MessageSerializer,
        404: {"detail": "The user does not exist."},
        400: {"detail": "You were not following this user."}
        },
)
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = MessageSerializer

    def delete(self, request, pk):
        request_user = request.user
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if not request_user.following.filter(followed=user).exists():
            return Response({'detail': 'You were not following this user.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            follow = Follow.objects.get(follower=request_user, followed=user)
            follow.delete()
            serializer = MessageSerializer({'message': 'You have successfully unfollowed the user.'})
            return Response(serializer.data, status=status.HTTP_200_OK)

unfollow_user_view = UnfollowUserView.as_view()


class FollowerListView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowerSerializer
    filterset_class = FollowerFilter
    
    def get_queryset(self):
        user_followed_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(followed_id=user_followed_id)
         
follower_list_view = FollowerListView.as_view()


class FollowedListView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowedSerializer
    filterset_class = FollowedFilter

    def get_queryset(self):
        user_follower_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(follower_id=user_follower_id)
         
followed_list_view = FollowedListView.as_view()
