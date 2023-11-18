from rest_framework import generics
from posts.models import Post, Tag
from posts.serializers import PostSerializer, TagSerializer
# Create your views here.

class ListCreatePost(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
            
list_create_post_view = ListCreatePost.as_view()

