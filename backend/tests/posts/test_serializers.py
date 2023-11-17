from rest_framework.test import APITestCase, APIRequestFactory
from posts.models import Post
from posts.serializers import PostSerializer, TagSerializer
from tests.posts.factories import PostFactory, TagFactory
from tests.accounts.factories import UserFactory


class TestUserSerializer(APITestCase):    
    def setUp(self) -> None:
        self.user = UserFactory()
        self.tags = TagFactory.create_batch(3)
        self.post = PostFactory()
        self.post.tags.set(self.tags)
        self.serializer = PostSerializer(self.post)
        
    def test_post_object_serialized(self):
        expected = {
            'id': self.post.id,
            'title': self.post.title,
            'content': self.post.content,
            'author': self.post.author.id,
            'nested_tags': [{'id': tag.id, 'name': tag.name} for tag in self.tags],
            'created_at': self.post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'total_likes': self.post.total_likes,
            'total_tags': self.post.total_tags,
            'total_comments': self.post.total_comments,
        }
        self.assertDictEqual(self.serializer.data, expected)

    def test_post_data_serialized(self):
        data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'tags': [tag.id for tag in self.tags],
        }
        request = APIRequestFactory('/')
        request.user = self.user
        serializer = PostSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        post_instance = serializer.save()

        self.assertEqual(post_instance.title, data['title'])
        self.assertEqual(post_instance.content, data['content'])
        self.assertEqual(post_instance.author.id, request.user.id)
        self.assertListEqual(list(post_instance.tags.all()), self.tags)

    