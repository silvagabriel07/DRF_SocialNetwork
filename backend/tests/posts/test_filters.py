from rest_framework.test import APITestCase    
from rest_framework import status
from tests.accounts.factories import UserFactory
from tests.posts.factories import PostFactory, TagFactory
from django.urls import reverse
from django.utils import timezone

timezone
class TestPostFilter(APITestCase):
    def setUp(self) -> None:
        user1 = UserFactory(username='JohnDoe')
        user1.profile.name = 'Paulo'
        user1.profile.save()
        self.tags = TagFactory.create_batch(2)
        self.post1 = PostFactory(author=user1, title='potato and salmon', content='lorem ipsum 1')
        self.post1.tags.set(self.tags)
        
        user2 = UserFactory(username='JaneDoe')
        user2.profile.name = 'Paula'
        user2.profile.save()
        self.post2 = PostFactory(author=user2, title='salmon and pineapple', content='lorem ipsum 2')
        self.post2.tags.add(self.tags[1])

        self.endpoint_using_the_filter = reverse('post-list-create')
        
    def test_search_post_field_filtering_by_profile_name(self):
        params = {'search_author': 'Paulo'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')
    
    def test_search_author_field_filtering_by_username(self):
        params = {'search_author': 'John'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')
        
    def test_search_post_field_filtering_by_title(self):
        params = {'search_post': 'potato'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')

    def test_search_post_field_filtering_by_content(self):
        params = {'search_post': '1'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')
    
    def test_tags_filter_field(self):
        params = {'tags': [self.tags[0].id, self.tags[1].id]}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')
    
    def test_created_at_filter_field(self):        
        self.post1.created_at += timezone.timedelta(days=10)
        self.post1.save()

        params = {'created_at_after': timezone.now() + timezone.timedelta(days=9), 'created_at_before': timezone.now() + timezone.timedelta(days=11)}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'potato and salmon')
        self.assertNotContains(response, 'salmon and pineapple')


# Post
# filter the post by the:
# 	title - icontains
# 	content - icontains
	
# 	author__profile__name - icontains
# 	author__username - icontains
	
# 	tags_name - icontains
	
# 	created_at - range
