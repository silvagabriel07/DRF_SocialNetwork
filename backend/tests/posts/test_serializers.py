from rest_framework.test import APITestCase, APIRequestFactory
from posts.serializers import PostSerializer, PostUpdateSerializer, TagSerializer, CommentSerializer, CommentLikeSerializer, PostLikeSerializer
from tests.posts.factories import PostFactory, TagFactory, CommentFactory, CommentLikeFactory, PostLikeFactory
from tests.accounts.factories import UserFactory
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as validaerr

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
        
    def test_update_post_adding_more_than_30_tags_fails(self):
        self.post.tags.add(TagFactory())
        tags = [tag.id for tag in TagFactory.create_batch(30)]
        data = {
            'title': 'Updated title',
            'content': 'Updated content',
            'tags': tags
        }
        serializer = PostUpdateSerializer(instance=self.post, data=data)
        with self.assertRaisesMessage(ValidationError, "A post can't have more than 30 tags."):
            serializer.is_valid(raise_exception=True)
        self.assertEqual(self.post.tags.all().count(), 1)
        
        
class TestTagSerializer(APITestCase):
    def setUp(self) -> None:
        self.tag = TagFactory()
    
    def test_data_returned(self):
        serializer = TagSerializer(self.tag)
        expected = {'id': self.tag.id, 'name': self.tag.name}
        self.assertEqual(serializer.data, expected)
        

class TestCommentSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory()
        self.comment = CommentFactory(post=self.post)
    
    def test_comment_object_serialized(self):
        serializer = CommentSerializer(self.comment)
        expected = {
            'post': self.comment.post.id,
            'id': self.comment.id,
            'author': self.comment.author.id,
            'content': self.comment.content,
            'created_at': self.comment.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'total_likes': 0,
        }
        self.assertEqual(serializer.data, expected)
    
    def test_comment_data_serialized(self):
        request = APIRequestFactory('/')
        request.user = self.user1
        data = {
            'content': 'lorem ipsunm content',
            'post': self.post.id,
        }
        serializer = CommentSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        comment_instance = serializer.save()
        self.assertEqual(comment_instance.content, data['content'])
        self.assertEqual(comment_instance.post.id, data['post'])
        self.assertEqual(comment_instance.author.id, self.user1.id)
        
        
class TestCommentLikeSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.comment = CommentFactory()

    def test_data_returned(self):
        commentlike = CommentLikeFactory(user=self.user1, comment=self.comment)
        expected = {
            'id': commentlike.id,
            'comment': self.comment.id,
            'user': self.user1.id,
            'created_at': commentlike.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        serializer = CommentLikeSerializer(commentlike)
        self.assertEqual(serializer.data, expected)
        

class TestPostLikeSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory()

    def test_data_returned(self):
        postlike = PostLikeFactory(user=self.user1, post=self.post)
        expected = {
            'id': postlike.id,
            'post': self.post.id,
            'user': self.user1.id,
            'created_at': postlike.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        serializer = PostLikeSerializer(postlike)
        self.assertEqual(serializer.data, expected)