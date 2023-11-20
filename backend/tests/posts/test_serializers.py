from rest_framework.test import APITestCase, APIRequestFactory
from posts.models import Post
from posts.serializers import PostSerializer, PostUpdateSerializer
from tests.posts.factories import PostFactory, TagFactory
from tests.accounts.factories import UserFactory


class TestPostSerializer(APITestCase):    
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


class TestPostUpdateSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.post = PostFactory()
        self.serializer = PostUpdateSerializer(self.post)

    def test_post_data_updated_serialized(self):
        tags = [tag.id for tag in TagFactory.create_batch(3)]
        data = {
            'title': 'Updated title',
            'content': 'Updated content',
            'tags': tags
        }
        serializer = PostSerializer(instance=self.post, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.post.refresh_from_db()
        self.assertEqual(data['title'], self.post.title)
        self.assertEqual(data['content'], self.post.content)
        self.assertEqual(data['tags'], [tag.id for tag in self.post.tags.all()])
        expected = {
            'id': self.post.id,
            'title': self.post.title,
            'content': self.post.content,
            'author': self.post.author.id,
            'nested_tags': [{'id': tag.id, 'name': tag.name} for tag in self.post.tags.all()],
            'created_at': self.post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'total_likes': self.post.total_likes,
            'total_tags': self.post.total_tags,
            'total_comments': self.post.total_comments,
        }
        self.assertEqual(serializer.data, expected)
        
        
        

