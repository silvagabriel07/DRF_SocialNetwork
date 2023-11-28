from django_filters import rest_framework as filters
from django.db.models import Q
from posts.models import Post, Tag, Comment, PostLike, CommentLike


class PostFilter(filters.FilterSet):
    class Meta:
        model = Post
        fields = ['search_author', 'search_post', 'tags', 'created_at']
        
    created_at = filters.DateTimeFromToRangeFilter()
    tags = filters.ModelMultipleChoiceFilter(field_name='tags', queryset=Tag.objects.all(), conjoined=True)
    search_author = filters.CharFilter(method='filter_search_author', label='Search by Profile Name or Username of the Post Author')
    search_post = filters.CharFilter(method='filter_search_post', label='Search by Title or Content')
        
    def filter_search_author(self, queryset, name, value):
        return queryset.filter(
            Q(author__profile__name__icontains=value) | Q(author__username__icontains=value)
        )
        
    def filter_search_post(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(content__icontains=value)
        )


class TagFilter(filters.FilterSet):
    class Meta:
        model = Tag
        fields = ['name']
    
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    

class CommentFilter(filters.FilterSet):
    class Meta:
        model = Comment
        fields = ['content', 'search_author', 'created_at']

    content = filters.CharFilter(field_name='content', lookup_expr='icontains')
    search_author = filters.CharFilter(method='filter_search_author', label='Search by Profile Name or Username of the Comment Author')
    created_at = filters.DateTimeFromToRangeFilter()

    def filter_search_author(self, queryset, name, value):
        return queryset.filter(
            Q(author__profile__name__icontains=value) | Q(author__username__icontains=value)
        )

class PostLikeFilter(filters.FilterSet):
    class Meta:
        model = PostLike
        fields = ['search_user']

    search_user = filters.CharFilter(method='filter_search_user', label='Search by Profile Name or Username')

    def filter_search_user(self, queryset, name, value):
        return queryset.filter(
            Q(user__profile__name__icontains=value) | Q(user__username__icontains=value)
        )
        
class CommentLikeFilter(filters.FilterSet):
    class Meta:
        model = CommentLike
        fields = ['search_user']

    search_user = filters.CharFilter(method='filter_search_user', label='Search by Profile Name or Username')

    def filter_search_user(self, queryset, name, value):
        return queryset.filter(
            Q(user__profile__name__icontains=value) | Q(user__username__icontains=value)
        )
