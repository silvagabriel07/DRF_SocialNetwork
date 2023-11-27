from django_filters import rest_framework as filters
from django.db.models import Q
from accounts.models import User, Profile, Follow

class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ['username', 'is_active']
        
    username = filters.CharFilter(field_name='username', lookup_expr='icontains')


class ProfileFilter(filters.FilterSet):
    class Meta:
        model = Profile
        fields = ['search']

    search = filters.CharFilter(method='filter_search', label='Search by Profile Name or Bio or Username')
        
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(bio__icontains=value) | Q(user__username__icontains=value)
        )
        

class FollowerFilter(filters.FilterSet):
    class Meta:
        model = Follow
        fields = ['search', 'created_at']

    search = filters.CharFilter(method='filter_search', label='Search by Profile Name or Username')
    created_at = filters.DateFromToRangeFilter()
    
    def filter_search(self, queryset, name, value):     
        return queryset.filter(
            Q(follower__username__icontains=value) | Q(follower__profile__name__icontains=value)
        )
        
        
class FollowedFilter(filters.FilterSet):
    class Meta:
        model = Follow
        fields = ['search', 'created_at']

    search = filters.CharFilter(method='filter_search', label='Search by Profile Name or Username')
    created_at = filters.DateFromToRangeFilter()
    
    def filter_search(self, queryset, name, value):     
        return queryset.filter(
            Q(followed__username__icontains=value) | Q(followed__profile__name__icontains=value)
        )

