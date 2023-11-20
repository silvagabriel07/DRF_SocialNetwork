from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_create_view, name='post-list-create'),
    path('post-detail/<int:pk>/', views.post_detail_view, name='post-detail'),
    path('post-update/<int:pk>/', views.post_update_view, name='post-update'),
    path('post-delete/<int:pk>/', views.post_delete_view, name='post-delete'),
]