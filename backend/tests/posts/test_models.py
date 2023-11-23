from rest_framework.test import APITestCase, APITransactionTestCase
from posts.models import Post, Tag
from tests.accounts.factories import UserFactory
from tests.posts.factories import PostFactory, PostLikeFactory, TagFactory, CommentFactory, CommentLikeFactory
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.utils import timezone


class TestPost(APITransactionTestCase):
    def setUp(self) -> None:
        self.post = PostFactory()

    def test_return_total_likes(self):
        for c in range(3):
            PostLikeFactory(post=self.post)
        self.assertEqual(self.post.total_likes, 3)
        
    def test_return_total_tags(self):
        tags = TagFactory.create_batch(3)    
        self.post.tags.set(tags)
        self.assertEqual(self.post.total_tags, 3)
        
    def test_return_total_comments(self):
        for c in range(3):
            CommentFactory(post=self.post)
        self.assertEqual(self.post.total_comments, 3)
        
    def test_post_with_more_than_30_tags_fails(self):
        tags30 = TagFactory.create_batch(30)
        self.post.tags.set(tags30)
        with self.assertRaisesMessage(ValidationError, "A post can't have more than 30 tags."):
            tag31 = TagFactory()
            self.post.tags.add(tag31)
        self.assertEqual(self.post.tags.all().count(),30)
        
    def test_update_post_more_than_twice_fails(self):
        self.post.title = 'title updated'
        self.post.save()
        self.assertTrue(self.post.edited)
        with self.assertRaisesMessage(ValidationError, 'This post has already been edited.'):
            self.post.title = 'title updated again'
            self.post.save()
    
    @patch('posts.models.timezone')
    def test_update_post_after_12_hours_fails(self, mock_timezone):
        mock_timezone.now.return_value = timezone.now() + timezone.timedelta(days=1)
        mock_timezone.timedelta.return_value = timezone.timedelta(hours=12)
        self.post.title = 'title updated'
        with self.assertRaisesMessage(ValidationError, 'This post cannot be edited any further.'):
            self.post.save()

                

class TestComment(APITestCase):
    def setUp(self) -> None:
        self.comment = CommentFactory()

    def test_return_total_likes(self):
        for c in range(3):
            CommentLikeFactory(comment=self.comment)
        self.assertEqual(self.comment.total_likes, 3)
        
    