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
                

class TestComment(APITestCase):
    def setUp(self) -> None:
        self.comment = CommentFactory()

    def test_return_total_likes(self):
        for c in range(3):
            CommentLikeFactory(comment=self.comment)
        self.assertEqual(self.comment.total_likes, 3)
        
    