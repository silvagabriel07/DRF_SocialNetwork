from rest_framework import generics, status, permissions
from rest_framework.views import Response
from drf_spectacular.utils import extend_schema
from posts.models import Post, Tag, Comment, CommentLike, PostLike
from posts import serializers
from accounts.serializers import MessageSerializer
from posts.filters import PostFilter, TagFilter, CommentFilter, PostLikeFilter, CommentLikeFilter
from accounts.permissions import IsObjectAuthor
# Create your views here.

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    filterset_class = PostFilter
            
post_list_create_view = PostListCreateView.as_view()


class PostFeedView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        followed_users = user.following.all().values('followed')
        qs = super().get_queryset()
        return qs.filter(author__in=followed_users).order_by('-created_at')
        
post_feed_view = PostFeedView.as_view()


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer
    
post_detail_view = PostDetailView.as_view()


class PostUpdateView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostUpdateSerializer
    permission_classes = [IsObjectAuthor]
    
post_update_view = PostUpdateView.as_view()


class PostDeleteView(generics.DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostDeleteSerializer
    permission_classes = [IsObjectAuthor]

post_delete_view = PostDeleteView.as_view()


@extend_schema(
    summary="Like a Post",
    description="Endpoint for liking a specific post.",
    responses={
        201: MessageSerializer,
        404: {"detail": "The post does not exist."},
        400: {"detail": "You are already liking this post."}
        },
)
class LikePostView(generics.CreateAPIView):
    queryset = PostLike.objects.all()
    serializer_class = serializers.PostLikeSerializer
    
    def create(self, request, *args, **kwargs):
        post_id = self.kwargs['pk']
        if not Post.objects.filter(id=post_id).exists():
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        request.data['post'] = post_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        message = MessageSerializer({'message': 'You have successfully liked the post.'})

        headers = self.get_success_headers(serializer.data)
        return Response(message.data, status=status.HTTP_201_CREATED, headers=headers)

like_post_view = LikePostView.as_view()


@extend_schema(
    summary="Dislike a Post",
    description="Endpoint for disliking a specific post.",
    responses={
        200: MessageSerializer,
        404: {"detail": "The post does not exist."},
        400: {"detail": "You were not liking this post."}
        },
)
class DislikePostView(generics.DestroyAPIView):
    serializer_class = MessageSerializer
    
    def destroy(self, request, *args, **kwargs):
        post_id = self.kwargs['pk']
    
        if not Post.objects.filter(id=post_id).exists():
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        instance = PostLike.objects.filter(post_id=post_id, user=request.user.id)    
        if not instance.exists():
            return Response({'detail': 'You were not liking this post.'}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.first().delete()
        message = MessageSerializer({'message': 'You have successfully disliked the post.'})

        return Response(message.data, status=status.HTTP_200_OK)
            
dislike_post_view = DislikePostView.as_view()


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    filterset_class = TagFilter

tag_list_view = TagListView.as_view()


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
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
    
comment_list_create_view = CommentListCreateView.as_view()


class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(id=comment_id)

    
comment_detail_view = CommentDetailView.as_view()


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsObjectAuthor]

comment_delete_view = CommentDeleteView.as_view()


@extend_schema(
    summary="Like a Comment",
    description="Endpoint for liking a specific comment.",
    responses={
        201: MessageSerializer,
        404: {"detail": "The comment does not exist."},
        400: {"detail": "You are already liking this comment."}
        },
)
class LikeCommentView(generics.CreateAPIView):
    queryset = CommentLike.objects.all()
    serializer_class = serializers.CommentLikeSerializer
    
    def create(self, request, *args, **kwargs):
        comment_id = self.kwargs['pk']
        if not Comment.objects.filter(id=comment_id).exists():
            return Response({'detail': 'The post does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        request.data['comment'] = comment_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        message = MessageSerializer({'message': 'You have successfully liked the comment.'})

        headers = self.get_success_headers(serializer.data)
        return Response(message.data, status=status.HTTP_201_CREATED, headers=headers)
    

like_comment_view = LikeCommentView.as_view()


@extend_schema(
    summary="Dislike a Comment",
    description="Endpoint for disliking a specific comment.",
    responses={
        200: MessageSerializer,
        404: {"detail": "The comment does not exist."},
        400: {"detail": "You were not liking this comment."}
        },
)
class DislikeCommentView(generics.DestroyAPIView):
    serializer_class = MessageSerializer

    def destroy(self, request, *args, **kwargs):
        comment_id = self.kwargs['pk']
    
        if not Comment.objects.filter(id=comment_id).exists():
            return Response({'detail': 'The comment does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        instance = CommentLike.objects.filter(comment_id=comment_id, user=request.user.id)    
        if not instance.exists():
            return Response({'detail': 'You were not liking this comment.'}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.first().delete()
        message = MessageSerializer({'message': 'You have successfully disliked the comment.'})

        return Response(message.data, status=status.HTTP_200_OK)
            
dislike_comment_view = DislikeCommentView.as_view()


class CommentLikeListView(generics.ListAPIView):
    queryset = CommentLike.objects.all()
    serializer_class = serializers.CommentLikeSerializer
    filterset_class = CommentLikeFilter
    
    def get_queryset(self):
        comment_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(comment_id=comment_id)
        
comment_like_list_view = CommentLikeListView.as_view()


class PostLikeListView(generics.ListAPIView):
    queryset = PostLike.objects.all()
    serializer_class = serializers.PostLikeSerializer
    filterset_class = PostLikeFilter
    
    def get_queryset(self):
        post_id = self.kwargs['pk']
        qs = super().get_queryset()
        return qs.filter(post_id=post_id)
        
post_like_list_view = PostLikeListView.as_view()