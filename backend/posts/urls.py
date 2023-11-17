from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_create_post_view, name='post-list-create')
]