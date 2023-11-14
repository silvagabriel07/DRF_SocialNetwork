from django.urls import path
from . import views

urlpatterns = [
    path('user-detail/<int:pk>/', views.user_detail_view, name='user-detail'),
    path('', views.user_list_view, name='user-list'),
    path('user-registration/', views.user_registration_view, name='user-registration'),
    path('user-update/<int:pk>', views.user_update_view, name='user-update'),
    path('user-delete/<int:pk>', views.user_delete_view, name='user-delete'),
    
    path('profile-detail/<int:pk>/', views.profile_detail_view, name='profile-detail')
]