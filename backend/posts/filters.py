from django_filters import rest_framework as filters
from django.db.models import Q
from posts.models import Post, Tag


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

# Post
# filter the post by the:
# 	title - icontains
# 	content - icontains
	
# 	author__profile__name - icontains
# 	author__username - icontains
	
# 	tags_name - exact
	
# 	created_at - range
