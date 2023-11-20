from rest_framework import generics, status
from rest_framework.views import Response
from posts.models import Post, Tag
from posts.serializers import PostSerializer, PostUpdateSerializer
# Create your views here.

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
            
post_list_create_view = PostListCreate.as_view()


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
post_detail_view = PostDetail.as_view()


class PostUpdate(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        post = self.get_object()
        print(post.author)
        if not request.user == post.author:
            print('qqaa')
            print(request.user)
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        return super().update(request, *args, **kwargs)

post_update_view = PostUpdate.as_view()


class PostDelete(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
        
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        
        if not request.user == post.author:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)

post_delete_view = PostDelete.as_view()
