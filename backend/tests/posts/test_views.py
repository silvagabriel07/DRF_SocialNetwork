from rest_framework.test import APITestCase
from tests.posts.factories import PostFactory, TagFactory
from tests.accounts.factories import UserFactory

from posts.models import Post
from posts.serializers import PostSerializer
from django.urls import reverse
from rest_framework import status

class TestListCreatePost(APITestCase):
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
        
