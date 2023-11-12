from django.urls import path
from . import views

urlpatterns = [
    path('user-detail/<int:pk>/', views.user_detail_view, name='user-detail'),
    path('', views.user_list_create_view, name='user-list-create'),
    
    path('profile-detail/<int:pk>/', views.profile_detail_view, name='profile-detail')
]