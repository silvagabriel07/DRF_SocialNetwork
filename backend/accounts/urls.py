from django.urls import path
from . import views

urlpatterns = [
    path('user-detail/<int:pk>/', views.user_detail_view, name='user-detail'),
    path('profile-detail/<int:pk>/', views.profile_detail_view, name='profile-detail')
]