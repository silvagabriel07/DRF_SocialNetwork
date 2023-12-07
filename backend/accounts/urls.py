from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # jwt authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    
    # users
    path('users/<int:pk>/', views.user_detail_view, name='user-detail'),
    path('users/', views.user_list_view, name='user-list'),
    path('users/register/', views.user_registration_view, name='user-registration'),
    path('users/<int:pk>/update/', views.user_update_view, name='user-update'),
    path('users/<int:pk>/delete/', views.user_delete_view, name='user-delete'),

    # profiles
    path('profiles/<int:pk>/', views.profile_detail_view, name='profile-detail'),
    path('profiles/<int:pk>/update/', views.profile_update_view, name='profile-update'),
    path('profiles/', views.profile_list_view, name='profile-list'),

    # following/unfollowing users
    path('users/<int:pk>/follow/', views.follow_user_view, name='follow-user'),
    path('users/<int:pk>/unfollow/', views.unfollow_user_view, name='unfollow-user'),

    # listing followers and followed
    path('users/<int:pk>/followers/', views.follower_list_view, name='follower-list'),
    path('users/<int:pk>/followed/', views.followed_list_view, name='followed-list'),
]
