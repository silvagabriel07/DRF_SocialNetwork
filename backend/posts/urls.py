from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_create_view, name='post-list-create'),
    path('post-detail/<int:pk>/', views.post_detail_view, name='post-detail'),
    path('post-update/<int:pk>/', views.post_update_view, name='post-update'),
    path('post-delete/<int:pk>/', views.post_delete_view, name='post-delete'),
    path('tag-list/', views.tag_list_view, name='tag-list'),

    path('like-post/<int:pk>/', views.like_post_view, name='like-post'),
    path('dislike-post/<int:pk>/', views.dislike_post_view, name='dislike-post'),
    
    path('<int:pk>/comment/', views.comment_list_create_view, name='comment-list-create'),
    path('comment-detail/<int:pk>/', views.comment_detail_view, name='comment-detail'),
    path('comment-delete/<int:pk>/', views.comment_delete_view, name='comment-delete'),

    path('like-comment/<int:pk>/', views.like_comment_view, name='like-comment'),
    path('dislike-comment/<int:pk>/', views.dislike_comment_view, name='dislike-comment'),

]