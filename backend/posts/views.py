from rest_framework import generics
from posts.models import Post, Tag
from posts.serializers import PostSerializer, TagSerializer
# Create your views here.

class ListCreatePost(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
            
list_create_post_view = ListCreatePost.as_view()
