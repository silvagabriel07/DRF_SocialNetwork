from django.urls import path
from . import views

urlpatterns = [
    # posts
    path('', views.post_list_create_view, name='post-list-create'),
    path('feed/', views.post_feed_view, name='post-feed-list'),
    path('<int:pk>/', views.post_detail_view, name='post-detail'),
    path('<int:pk>/update/', views.post_update_view, name='post-update'),
    path('<int:pk>/delete/', views.post_delete_view, name='post-delete'),
    path('<int:pk>/like-list/', views.post_like_list_view, name='post-like-list'),    

    # tags
    path('tags/', views.tag_list_view, name='tag-list'),

    # liking and disliking posts 
    path('<int:pk>/like/', views.like_post_view, name='like-post'),
    path('<int:pk>/dislike/', views.dislike_post_view, name='dislike-post'),
    
    # comments in posts
    path('<int:pk>/comments/', views.comment_list_create_view, name='comment-list-create'),
    path('comments/<int:pk>/', views.comment_detail_view, name='comment-detail'),
    path('comments/<int:pk>/delete/', views.comment_delete_view, name='comment-delete'),
    path('comments/<int:pk>/like-list/', views.comment_like_list_view, name='comment-like-list'),    

    # liking and disliking comments
    path('comments/<int:pk>/like/', views.like_comment_view, name='like-comment'),
    path('comments/<int:pk>/dislike/', views.dislike_comment_view, name='dislike-comment'),
]
