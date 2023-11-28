from rest_framework.test import APITestCase    
from rest_framework import status
from tests.accounts.factories import UserFactory
from tests.posts.factories import PostFactory, TagFactory, CommentFactory, PostLikeFactory, CommentLikeFactory
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
        
    def test_search_author_field_filtering_by_profile_name(self):
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


class TestTagFilter(APITestCase):
    def setUp(self) -> None:
        self.tag1 = TagFactory(name='Paul')
        self.tag2 = TagFactory(name='Shell')

        self.endpoint_using_the_filter = reverse('tag-list')

    def test_created_at_filter_field_(self):
        params = {'name': 'll'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Shell')
        self.assertNotContains(response, 'Paul')
        
        
class TestCommentFilter(APITestCase):
    def setUp(self) -> None:
        post = PostFactory()
        self.user1 = UserFactory(username='John')
        self.user1.profile.name = 'Aka'
        self.user1.profile.save()
        self.comment1 = CommentFactory(author=self.user1, post=post, content='content 2')
        
        self.user2 = UserFactory(username='Jane')
        self.user2.profile.name = 'Akasaka'
        self.user2.profile.save()
        self.comment2 = CommentFactory(author=self.user2, post=post, content='content 1')
        self.endpoint_using_the_filter = reverse('comment-list-create', args=[post.id])

    def test_content_filter_field(self):
        params = {'content': '1'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'content 1')
        self.assertNotContains(response, 'content 2')

    def test_search_author_field_filtering_by_username(self):
        params = {'search_author': 'ne'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'content 1')
        self.assertNotContains(response, 'content 2')
        
    def test_search_author_field_filtering_by_name(self):
        params = {'search_author': 'saka'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'content 1')
        self.assertNotContains(response, 'content 2')
        
    def test_created_at_filter_field(self):        
        self.comment2.created_at += timezone.timedelta(days=10)
        self.comment2.save()

        params = {'created_at_after': timezone.now() + timezone.timedelta(days=9), 'created_at_before': timezone.now() + timezone.timedelta(days=11)}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content 1')
        self.assertNotContains(response, 'content 2')


class TestPostLikeFilter(APITestCase):
    def setUp(self) -> None:
        post = PostFactory()
        
        self.user1 = UserFactory(username='John')
        self.user1.profile.name = 'Fujiwara'
        self.user1.profile.save()
        self.like1 = PostLikeFactory(post=post, user=self.user1)
        
        self.user2 = UserFactory(username='Jane')
        self.user2.profile.name = 'Akasaka'
        self.user2.profile.save()
        self.like2 = PostLikeFactory(post=post, user=self.user2)
        self.endpoint_using_the_filter = reverse('post-like-list', args=[post.id])
    
    def test_search_user_field_filtering_by_username(self):
        params = {'search_user': 'ne'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Jane')
        self.assertNotContains(response, 'John')
        
    def test_search_user_field_filtering_by_name(self):
        params = {'search_user': 'saka'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Akasaka')
        self.assertNotContains(response, 'Fujiwara')


class TestCommentFilter(APITestCase):
    def setUp(self) -> None:
        comment = CommentFactory()
        
        self.user1 = UserFactory(username='John')
        self.user1.profile.name = 'Fujiwara'
        self.user1.profile.save()
        self.like1 = CommentLikeFactory(comment=comment, user=self.user1)
        
        self.user2 = UserFactory(username='Jane')
        self.user2.profile.name = 'Akasaka'
        self.user2.profile.save()
        self.like2 = CommentLikeFactory(comment=comment, user=self.user2)
        self.endpoint_using_the_filter = reverse('comment-like-list', args=[comment.id])
    
    def test_search_user_field_filtering_by_username(self):
        params = {'search_user': 'ne'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Jane')
        self.assertNotContains(response, 'John')
        
    def test_search_user_field_filtering_by_name(self):
        params = {'search_user': 'saka'}
        response = self.client.get(self.endpoint_using_the_filter, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'Akasaka')
        self.assertNotContains(response, 'Fujiwara')
