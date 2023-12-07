from rest_framework.test import APITestCase
from accounts.models import User, Profile, Follow
from tests.accounts.factories import UserFactory, FollowFactory
from tests.posts.factories import PostFactory
from django.core.exceptions import ValidationError

class TestProfileFollowMethods(APITestCase):
    def setUp(self) -> None:
        for i in range(1, 3):
            User.objects.create_user(username=f'user {i}', password=f'password{i}', email=f'email{i}@gmail.com')
        self.user2 = User.objects.get(username='user 2')
        user1 = User.objects.get(username='user 1')
        self.prof1 = Profile.objects.get(user=user1)

    def test_create_user_creates_user_profile(self):
        user3 = User.objects.create_user(username='user 3', password='password3', email='email3@gmail.com')
        self.assertTrue(Profile.objects.filter(user=user3))
    
    def test_return_total_posts_property(self):
        PostFactory(author=self.user2)
        count_posts = self.user2.posts.all().count()
        self.assertEqual(self.user2.profile.total_posts, count_posts)
            
    def test_total_followers_property(self):
        FollowFactory(follower=self.user2, followed=self.prof1.user)
        count_followers = self.prof1.user.followers.all().count()
        self.assertEqual(self.prof1.total_followers, count_followers)
     
    def test_total_following_property(self):
        FollowFactory(follower=self.prof1.user, followed=self.user2)
        count_following = self.prof1.user.following.all().count()
        self.assertEqual(self.prof1.total_following, count_following)
                

class TestFollow(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        
    def test_follow_user_successfully(self):
        Follow.objects.create(follower=self.user1, followed=self.user2)
        self.assertEqual(self.user1.following.first().followed, self.user2)
        self.assertEqual(self.user2.followers.first().follower, self.user1)
        
    def test_user_cannot_follow_themselves(self):
        with self.assertRaisesMessage(ValidationError, 'You can not follow yourself.'):
            Follow.objects.create(
                follower=self.user1,
                followed=self.user1
            )