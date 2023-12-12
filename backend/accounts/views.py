from rest_framework import generics, permissions, status
from rest_framework.views import Response
from accounts.models import User, Profile, Follow
from accounts import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.filters import UserFilter, ProfileFilter, FollowerFilter, FollowedFilter
from drf_spectacular.utils import extend_schema
from accounts.permissions import IsUser
# Create your views here.

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    
user_detail_view = UserDetailView.as_view()


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    filterset_class = UserFilter
    
user_list_view = UserListView.as_view()


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserCreationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': self.get_serializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)

user_registration_view = UserRegistrationView.as_view()


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserUpdateSerializer
    permission_classes = [IsUser]
    
user_update_view = UserUpdateView.as_view()    


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsUser]

user_delete_view = UserDeleteView.as_view()    


class ProfileDetailView(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    
profile_detail_view = ProfileDetailView.as_view()


class ProfileListView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    filterset_class = ProfileFilter

profile_list_view = ProfileListView.as_view()


class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsUser]
    
profile_update_view = ProfileUpdateView.as_view()


@extend_schema(
    summary="Follow a User",
    description="Endpoint for follow a specific user.",
    responses={
        201: serializers.MessageSerializer,
        404: {"detail": "The user does not exist."},
        400: {"detail": "You are already following this user."},
        400: {"detail": "You can not follow yourself."},
        },
)
class FollowUserView(generics.CreateAPIView):
    queryset = Follow.objects.all()
    serializer_class = serializers.FollowSerializer


    def create(self, request, *args, **kwargs):
        user_id = self.kwargs['pk']
        if not User.objects.filter(id=user_id).exists():
            return Response({'detail': 'The user does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        request.data['followed'] = user_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        message = serializers.MessageSerializer({'message': 'You have successfully followed the user.'})
        headers = self.get_success_headers(serializer.data)
        return Response(message.data, status=status.HTTP_201_CREATED, headers=headers)
            
follow_user_view = FollowUserView.as_view()


@extend_schema(
    summary="Unfollow a User",
    description="Endpoint for unfollow a specific user.",
    responses={
        200: serializers.MessageSerializer,
        404: {"detail": "The user does not exist."},
        400: {"detail": "You were not following this user."}
        },
)
class UnfollowUserView(generics.DestroyAPIView):
    serializer_class = serializers.MessageSerializer

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
            serializer = serializers.MessageSerializer({'message': 'You have successfully unfollowed the user.'})
            return Response(serializer.data, status=status.HTTP_200_OK)

unfollow_user_view = UnfollowUserView.as_view()


class FollowerListView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = serializers.FollowerSerializer
    filterset_class = FollowerFilter
    
    def get_queryset(self):
        user_followed_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(followed_id=user_followed_id)
         
follower_list_view = FollowerListView.as_view()


class FollowedListView(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = serializers.FollowedSerializer
    filterset_class = FollowedFilter

    def get_queryset(self):
        user_follower_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(follower_id=user_follower_id)
         
followed_list_view = FollowedListView.as_view()


