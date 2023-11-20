from rest_framework.test import APITestCase
from tests.posts.factories import PostFactory, TagFactory, PostLikeFactory
from tests.accounts.factories import UserFactory

from posts.models import Post
from posts.serializers import PostSerializer
from django.urls import reverse
from rest_framework import status

class TestPostListCreate(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('post-list-create')
        self.user1 = UserFactory()
        self.client.force_login(self.user1)

        self.tags = TagFactory.create_batch(3)
    
    def test_list_all_nested_tags_in_post(self):
        post = PostFactory()
        post.tags.set(self.tags)
        
        response = self.client.get(self.url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = [{'id': tag.id, 'name': tag.name} for tag in post.tags.all()]
        ordered_nested_tags = [ordered_post['nested_tags'] for ordered_post in response.data]
        response_nested_tags_data = [{'id': tag['id'], 'name': tag['name']} for tag in ordered_nested_tags[0]]
        self.assertListEqual(response_nested_tags_data, expected)
    
    def test_list_all_posts(self):
        PostFactory.create_batch(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PostSerializer(Post.objects.all(), many=True)
        self.assertEqual(response.data, serializer.data) 


    def test_create_post_successfully(self):
        data = {
            'title': 'title 1',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'tags': [self.tags[0].id, self.tags[1].id, self.tags[2].id, ],
        }
        response = self.client.post(self.url, data=data, format='json')
        response.data.pop('nested_tags')
        expected = {
           'id': response.data['id'],
           'title': data['title'],
           'content': data['content'],
           'author': self.user1.id,
        #    'nested_tags': data['tags'],     We already test this field separetely.
           'created_at': response.data['created_at'],
           'total_likes': 0,
           'total_tags': len(data['tags']),
           'total_comments': 0
        }
        
        self.assertEqual(response.data, expected)
        post_created = Post.objects.get(id=expected['id'])
        self.assertEqual([tag.id for tag in post_created.tags.all()], data['tags'])
        
    def test_create_post_successfully(self):
        data = {
            'title': 'title 1',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'tags': [self.tags[0].id, self.tags[1].id, self.tags[2].id, ],
        }
        response = self.client.post(self.url, data=data, format='json')
        response.data.pop('nested_tags')
        expected = {
           'id': response.data['id'],
           'title': data['title'],
           'content': data['content'],
           'author': self.user1.id,
        #    'nested_tags': data['tags'],     We already test this field separetely.
           'created_at': response.data['created_at'],
           'total_likes': 0,
           'total_tags': len(data['tags']),
           'total_comments': 0
        }
        
        self.assertEqual(response.data, expected)
        post_created = Post.objects.get(id=expected['id'])
        self.assertEqual([tag.id for tag in post_created.tags.all()], data['tags'])


class TestPostDetail(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.client.force_login(self.user1)
        self.url = reverse('post-detail', args=[self.user1.id])

        self.tags = TagFactory.create_batch(3)

    def test_return_data(self):
        post = PostFactory()
        response = self.client.get(self.url)
        serializer = PostSerializer(post)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        

class TestPostUpdate(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory(author=self.user1)
        self.client.force_login(self.user1)
        self.url = reverse('post-update', args=[self.post.id])
    
    def test_patch_title_updated(self):
        data = {
            'title': 'Title updated'
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data['title'])

    def test_patch_content_updated(self):
        data = {
            'content': 'Content updated'
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], data['content'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, data['content'])
        
    def test_patch_tags_updated(self):
        all_tags = TagFactory.create_batch(3)
        tags = [tag.id for tag in all_tags]
        data = {
            'tags': tags
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nested_tags'], [{'id': tag.id, 'name': tag.name} for tag in all_tags])
        self.post.refresh_from_db()
        self.assertEqual(list(self.post.tags.all()), all_tags)
    
    def test_put_return_data(self):
        all_tags = TagFactory.create_batch(3)
        tags = [tag.id for tag in all_tags]
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
            'tags': tags
        }
        response = self.client.patch(self.url, data=data)
        expected = {
           'id': self.post.id,
           'title': data['title'],
           'content': data['content'],
           'author': self.user1.id,
           'nested_tags': [{'id': tag.id, 'name': tag.name} for tag in all_tags],
           'created_at': response.data['created_at'],
           'total_likes': 0,
           'total_tags': len(data['tags']),
           'total_comments': 0
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
    
    def test_update_post_user_of_the_request_must_be_the_owner(self):
        another_user = UserFactory()
        self.client.logout()
        self.client.force_login(another_user)
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
        }
        response = self.client.patch(self.url, data=data)
        expected = {
            'request.user': 'You are not authorized to perform this action.'
        }
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected)


class TestPostDelete(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.another_user = UserFactory()
        self.post = PostFactory(author=self.user1)
        self.url = reverse('post-delete', args=[self.post.id])
    
    def test_delete_post_user_of_the_request_must_be_the_owner(self):
        self.client.force_login(self.another_user)
        response = self.client.delete(self.url)
        expected = {
            'request.user': 'You are not authorized to perform this action.'
        }
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, expected)

    def test_delete_post_successfully(self):
        self.client.force_login(self.user1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.all().exists())


class TestLikePost(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.post = PostFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('like-post', args=[self.post.id])

    def test_like_post_successfully(self):
        response = self.client.post(self.url)
        expected = {
            'message': 'You have successfully liked the post.'
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.all().count(), 1)

    def test_like_post_already_liked_fails(self):
        PostLikeFactory(post=self.post, user=self.user1)
        response = self.client.post(self.url)
        expected = {
            'detail': 'You are already liking this post.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)
        self.assertEqual(self.post.likes.all().count(), 1)

    def test_like_post_with_pk_of_a_non_existing_post_fails(self):
        invalid_pk = 10
        url = reverse('like-post', args=[invalid_pk])
        response = self.client.post(url)
        expected = {
            'detail': 'The post does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)


class TestDislikePost(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.post = PostFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('dislike-post', args=[self.post.id])

    def test_dislike_post_successfully(self):
        PostLikeFactory(user=self.user1, post=self.post)
        response = self.client.delete(self.url)
        expected = {
            'message': 'You have successfully disliked the post.'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.all().count(), 0)

    def test_dislike_post_that_is_not_liked_fails(self):
        response = self.client.delete(self.url)
        expected = {
            'detail': 'You were not liking this post.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)

    def test_like_post_with_pk_of_a_non_existing_post_fails(self):
        invalid_pk = 10
        url = reverse('dislike-post', args=[invalid_pk])
        response = self.client.delete(url)
        expected = {
            'detail': 'The post does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)
