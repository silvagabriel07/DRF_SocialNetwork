from rest_framework.test import APITestCase, APIRequestFactory
from posts.serializers import PostSerializer, PostUpdateSerializer, TagSerializer, CommentSerializer, CommentLikeSerializer, PostLikeSerializer, ProfileSimpleSerializer
from tests.posts.factories import PostFactory, TagFactory, CommentFactory, CommentLikeFactory, PostLikeFactory
from tests.accounts.factories import UserFactory
from rest_framework.exceptions import ValidationError
from unittest.mock import patch
from django.utils import timezone
from posts.mixins import max_tags_allowed

class TestPostSerializer(APITestCase):    
    def setUp(self) -> None:
        self.user = UserFactory()
        self.tags = TagFactory.create_batch(3)
        self.post = PostFactory()
        self.post.tags.set(self.tags)
        factory = APIRequestFactory()
        self.request = factory.get('/')
        self.serializer = PostSerializer(self.post, context={'request': self.request})

        
    def test_post_object_initial_fields_serialized(self):
        expected = {
            'id': self.post.id,
            'title': self.post.title,
            'content': self.post.content,
            'author': ProfileSimpleSerializer(self.post.author.profile, context={'request': self.request}).data,
            'nested_tags': [{'id': tag.id, 'name': tag.name} for tag in self.tags],
            'created_at': self.post.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'total_likes': self.post.total_likes,
            'total_tags': self.post.total_tags,
            'total_comments': self.post.total_comments,
            'edited': self.post.edited
        }
        self.assertEqual(self.serializer.data['id'], expected['id'])
        self.assertEqual(self.serializer.data['title'], expected['title'])
        self.assertEqual(self.serializer.data['content'], expected['content'])
        self.assertEqual(self.serializer.data['created_at'], expected['created_at'])
        self.assertEqual(self.serializer.data['total_likes'], expected['total_likes'])
        self.assertEqual(self.serializer.data['total_tags'], expected['total_tags'])
        self.assertEqual(self.serializer.data['total_comments'], expected['total_comments'])
        self.assertEqual(self.serializer.data['edited'], expected['edited'])
        self.assertEqual(self.serializer.data['author'], expected['author'])
        self.assertEqual(self.serializer.data['nested_tags'], expected['nested_tags'])

    def test_create_post_data_serialized(self):
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
    
    def test_create_post_with_more_than_30_tags_fails(self):
        data = {
            'title': 'Test Title',
            'content': 'Test Content',
            'tags': [tag.id for tag in TagFactory.create_batch(31)],
        }
        request = APIRequestFactory('/')
        request.user = self.user
        serializer = PostSerializer(data=data, context={'request': request})
        with self.assertRaisesMessage(ValidationError, "A post can't have more than 30 tags."):
            serializer.is_valid(raise_exception=True)


class TestPostUpdateSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.post = PostFactory()
        factory = APIRequestFactory()
        self.request = factory.get('/')

    def test_post_data_updated_serialized(self):
        tags = [tag.id for tag in TagFactory.create_batch(3)]
        data = {
            'title': 'Updated title',
            'content': 'Updated content',
            'tags': tags
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.post.refresh_from_db()
        self.assertEqual(data['title'], self.post.title)
        self.assertEqual(data['content'], self.post.content)
        self.assertEqual(data['tags'], [tag.id for tag in self.post.tags.all()])
        self.assertTrue(self.post.edited)
        
    def test_update_post_adding_more_than_max_tags_allowed_tags_fails(self):
        self.post.tags.add(TagFactory())
        tags = [tag.id for tag in TagFactory.create_batch(max_tags_allowed)]
        data = {
            'title': 'Updated title',
            'content': 'Updated content',
            'tags': tags
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data)
        with self.assertRaisesMessage(ValidationError, f"A post can't have more than {max_tags_allowed} tags."):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(self.post.tags.all().count(), 1)

    def test_update_post_already_updated_fails(self):
        data = {
            'title': 'Updated title',
            'content': 'Updated content',
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.post.refresh_from_db()
        self.assertTrue(self.post.edited)
        
        data = {
            'title': 'Updated title again',
            'content': 'Updated content again',
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data)
        with self.assertRaisesMessage(ValidationError, 'This post has already been edited.'):
            serializer.is_valid(raise_exception=True)
    
    @patch('posts.mixins.timezone')
    def test_update_post_after_12_hours_fails(self, mock_timezone):
        mock_timezone.now.return_value = timezone.now() + timezone.timedelta(days=1)
        mock_timezone.timedelta.return_value = timezone.timedelta(hours=12)
        data = {
            'title': 'Updated title again',
            'content': 'Updated content again',
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data)
        with self.assertRaisesMessage(ValidationError, 'This post cannot be edited any further.'):
            serializer.is_valid(raise_exception=True)

        
class TestTagSerializer(APITestCase):
    def setUp(self) -> None:
        self.tag = TagFactory()
    
    def test_data_returned(self):
        serializer = TagSerializer(self.tag)
        expected = {'id': self.tag.id, 'name': self.tag.name}
        self.assertEqual(serializer.data['id'], expected['id'])
        self.assertEqual(serializer.data['name'], expected['name'])
        

class TestCommentSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory()
        self.comment = CommentFactory(post=self.post)
        factory = APIRequestFactory()
        self.request = factory.get('/')
        self.request.user = self.user1
    
    def test_comment_object_initial_fields_serialized(self):
        serializer = CommentSerializer(self.comment, context={'request': self.request})
        expected = {
            'post': self.comment.post.id,
            'id': self.comment.id,
            'author': ProfileSimpleSerializer(self.comment.author.profile, context={'request': self.request}).data,
            'content': self.comment.content,
            'created_at': self.comment.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'total_likes': 0,
        }
        self.assertEqual(serializer.data['post'], expected['post'])
        self.assertEqual(serializer.data['id'], expected['id'])
        self.assertEqual(serializer.data['author'], expected['author'])
        self.assertEqual(serializer.data['content'], expected['content'])
        self.assertEqual(serializer.data['created_at'], expected['created_at'])
        self.assertEqual(serializer.data['total_likes'], expected['total_likes'])

    
    def test_comment_data_serialized(self):
        data = {
            'content': 'lorem ipsunm content',
            'post': self.post.id,
        }
        serializer = CommentSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        comment_instance = serializer.save()
        self.assertEqual(comment_instance.content, data['content'])
        self.assertEqual(comment_instance.post.id, data['post'])
        self.assertEqual(comment_instance.author.id, self.user1.id)
        self.assertEqual(comment_instance.post.id, data['post'])
        
        
class TestCommentLikeSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.comment = CommentFactory()
        factory = APIRequestFactory()
        self.request = factory.get('/')
        self.request.user = self.user1

    def test_commentlike_object_initial_fields_serialized(self):
        commentlike = CommentLikeFactory(user=self.user1, comment=self.comment)
        expected = {
            'id': commentlike.id,
            'comment': self.comment.id,
            'profile': ProfileSimpleSerializer(self.user1.profile, context={'request': self.request}).data,
            'created_at': commentlike.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        serializer = CommentLikeSerializer(commentlike, context={'request': self.request})
        self.assertEqual(serializer.data['id'], expected['id'])
        self.assertEqual(serializer.data['comment'], expected['comment'])
        self.assertEqual(serializer.data['profile'], expected['profile'])
        self.assertEqual(serializer.data['created_at'], expected['created_at'])

    def test_commentlike_data_serialized(self):
        data = {
            'comment': self.comment.id,
        }
        serializer = CommentLikeSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        commentlike = serializer.save()
        self.assertEqual(serializer.data['comment'], data['comment'])
        self.assertEqual(commentlike.user, self.request.user)
        self.assertEqual(commentlike.comment.id, data['comment'])


class TestPostLikeSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory()
        factory = APIRequestFactory()
        self.request = factory.get('/')
        self.request.user = self.user1

    def test_postlike_object_initial_fields_serialized(self):
        postlike = PostLikeFactory(user=self.user1, post=self.post)
        expected = {
            'id': postlike.id,
            'post': self.post.id,
            'profile': ProfileSimpleSerializer(self.user1.profile, context={'request': self.request}).data,
            'created_at': postlike.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        serializer = PostLikeSerializer(postlike, context={'request': self.request})
        self.assertEqual(serializer.data['id'], expected['id'])
        self.assertEqual(serializer.data['post'], expected['post'])
        self.assertEqual(serializer.data['profile'], expected['profile'])
        self.assertEqual(serializer.data['created_at'], expected['created_at'])
        
    def test_postlike_data_serialized(self):
        data = {
            'post': self.post.id,
        }
        serializer = PostLikeSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        postlike = serializer.save()
        self.assertEqual(serializer.data['post'], data['post'])
        self.assertEqual(postlike.user, self.request.user)
        self.assertEqual(postlike.post.id, data['post'])
