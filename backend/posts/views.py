from rest_framework import generics, status
from rest_framework.views import Response, APIView
from posts.models import Post, Tag, Comment
from posts.serializers import PostSerializer, PostUpdateSerializer, LikePostSerializer
from accounts.serializers import MessageSerializer
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
        if not request.user == post.author:
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


class LikePost(generics.CreateAPIView):
    def post(self, request, pk):
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if post.likes.filter(user=user).exists():
            return Response({'detail': 'You are already liking this post.'}, status=status.HTTP_400_BAD_REQUEST)

        user.profile.like_post(post)
        serializer = MessageSerializer({'message': 'You have successfully liked the post.'})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

like_post_view = LikePost.as_view()


class DislikePost(generics.DestroyAPIView):
    def delete(self, request, pk):
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if not post.likes.filter(user=user).exists():
            return Response({'detail': 'You were not liking this post.'}, status=status.HTTP_400_BAD_REQUEST)

        user.profile.dislike_post(post)
        serializer = MessageSerializer({'message': 'You have successfully disliked the post.'})
        return Response(serializer.data, status=status.HTTP_200_OK)
            
dislike_post_view = DislikePost.as_view()
