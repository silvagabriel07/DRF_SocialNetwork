from django.urls import path
from . import views

urlpatterns = [
    path('user-detail/<int:pk>/', views.user_detail_view, name='user-detail'),
    path('user-list/', views.user_list_view, name='user-list'),
    path('user-registration/', views.user_registration_view, name='user-registration'),
    path('user-update/<int:pk>', views.user_update_view, name='user-update'),
    path('user-delete/<int:pk>', views.user_delete_view, name='user-delete'),
    
    path('profile-detail/<int:pk>/', views.profile_detail_view, name='profile-detail'),
    path('profile-update/<int:pk>/', views.profile_update_view, name='profile-update'),
    path('', views.profile_list_view, name='profile-list'),
    
    
]