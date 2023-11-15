from rest_framework.test import APITestCase
from accounts.models import User
from tests.posts.factories import PostFactory, PostLikeFactory, TagFactory
from tests.accounts.factories import UserFactory

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