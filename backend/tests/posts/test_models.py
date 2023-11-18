from rest_framework.test import APITestCase
from accounts.models import User
from tests.posts.factories import PostFactory, PostLikeFactory, TagFactory, CommentFactory, CommentLikeFactory

class TestPost(APITestCase):
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

        
class TestComment(APITestCase):
    def setUp(self) -> None:
        self.comment = CommentFactory()

    def test_return_total_likes(self):
        for c in range(3):
            CommentLikeFactory(comment=self.comment)
        self.assertEqual(self.comment.total_likes, 3)
        
    