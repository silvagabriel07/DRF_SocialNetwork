from rest_framework import generics, status
from rest_framework.views import Response
from posts.models import Post, Tag, Comment, CommentLike, PostLike
from posts.serializers import PostSerializer, PostUpdateSerializer, TagSerializer, CommentSerializer, CommentLikeSerializer, PostLikeSerializer
from accounts.serializers import MessageSerializer
from posts.filters import PostFilter, TagFilter, CommentFilter, PostLikeFilter, CommentLikeFilter
from drf_spectacular.utils import extend_schema
# Create your views here.

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filterset_class = PostFilter
            
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

@extend_schema(
    summary="Like a Post",
    description="Endpoint for liking a specific post.",
    responses={
        201: MessageSerializer,
        404: {"detail": "The post does not exist."},
        400: {"detail": "You are already liking this post."}
        },
)
class LikePost(generics.CreateAPIView):
    serializer_class = MessageSerializer
    
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


@extend_schema(
    summary="Dislike a Post",
    description="Endpoint for disliking a specific post.",
    responses={
        200: MessageSerializer,
        404: {"detail": "The post does not exist."},
        400: {"detail": "You were not liking this post."}
        },
)
class DislikePost(generics.DestroyAPIView):
    serializer_class = MessageSerializer
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


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filterset_class = TagFilter

tag_list_view = TagList.as_view()


class CommentListCreate(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filterset_class = CommentFilter
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(post_id=post_id)
        
    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        return serializer.save(author=self.request.user, post=post)
    
comment_list_create_view = CommentListCreate.as_view()


class CommentDetail(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(id=comment_id)

    
comment_detail_view = CommentDetail.as_view()


class CommentDelete(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
        
    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        
        if not request.user == comment.author:
            error_response = {'request.user': 'You are not authorized to perform this action.'}
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        
        return super().destroy(request, *args, **kwargs)

comment_delete_view = CommentDelete.as_view()


@extend_schema(
    summary="Like a Comment",
    description="Endpoint for liking a specific comment.",
    responses={
        201: MessageSerializer,
        404: {"detail": "The comment does not exist."},
        400: {"detail": "You are already liking this comment."}
        },
)
class LikeComment(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def post(self, request, pk):
        user = request.user
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'detail': 'The comment does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if comment.likes.filter(user=user).exists():
            return Response({'detail': 'You are already liking this comment.'}, status=status.HTTP_400_BAD_REQUEST)

        user.profile.like_comment(comment)
        serializer = MessageSerializer({'message': 'You have successfully liked the comment.'})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

like_comment_view = LikeComment.as_view()


@extend_schema(
    summary="Dislike a Comment",
    description="Endpoint for disliking a specific comment.",
    responses={
        200: MessageSerializer,
        404: {"detail": "The comment does not exist."},
        400: {"detail": "You were not liking this comment."}
        },
)
class DislikeComment(generics.DestroyAPIView):
    serializer_class = MessageSerializer

    def delete(self, request, pk):
        user = request.user
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'detail': 'The comment does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if not comment.likes.filter(user=user).exists():
            return Response({'detail': 'You were not liking this comment.'}, status=status.HTTP_400_BAD_REQUEST)

        user.profile.dislike_comment(comment)
        serializer = MessageSerializer({'message': 'You have successfully disliked the comment.'})
        return Response(serializer.data, status=status.HTTP_200_OK)
            
dislike_comment_view = DislikeComment.as_view()


class CommentLikeList(generics.ListAPIView):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    filterset_class = CommentLikeFilter
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(comment_id=comment_id)
        
comment_like_list_view = CommentLikeList.as_view()


class PostLikeList(generics.ListAPIView):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    filterset_class = PostLikeFilter
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(post_id=post_id)
        
post_like_list_view = PostLikeList.as_view()