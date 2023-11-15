from rest_framework.test import APITestCase 
from accounts.models import User, Profile, Follow
from tests.accounts.factories import UserFactory
from tests.posts.factories import PostFactory, TagFactory, PostLikeFactory
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class TestProfileFollowMethod(APITestCase):
    def setUp(self) -> None:
        for i in range(1, 3):
            User.objects.create_user(username=f'user {i}', password=f'password{i}', email=f'email{i}@gmail.com')
        self.user2 = User.objects.get(username='user 2')
        user1 = User.objects.get(username='user 1')
        self.prof1 = Profile.objects.get(user=user1)

    def test_create_user_creates_user_profile(self):
        user3 = User.objects.create_user(username='user 3', password='password3', email='email3@gmail.com')
        self.assertTrue(Profile.objects.filter(user=user3))

    def test_follow_method_users_following(self):
        self.prof1.follow(self.user2)
        all_following = self.prof1.user.following.all()
        self.assertEqual(all_following.count(), 1)
        self.assertEqual(all_following.first().followed, self.user2)
        all_followers = self.prof1.user.followers.all()
        self.assertFalse(all_followers.exists())
        
    def test_follow_method_users_followers(self):
        self.prof1.follow(self.user2)
        all_followers = self.user2.followers.all()
        self.assertEqual(all_followers.count(), 1)
        self.assertEqual(all_followers.first().follower.profile, self.prof1)
        all_following = self.user2.following.all()
        self.assertFalse(all_following.exists())
        
    def test_follow_method_self_following_fails(self):
        with self.assertRaisesMessage(ValidationError, 'User cannot follow themselves.'):
            self.prof1.follow(self.prof1.user)

    def test_follow_method_user_followed_twice_by_the_same_user(self):
        self.prof1.follow(self.user2)
        with self.assertRaisesMessage(ValidationError, 'You are already following this user.'):
            self.assertFalse(self.prof1.follow(self.user2))    
    
    def test_unfollow_method_user_following(self):
        self.prof1.follow(self.user2)
        all_followers = self.user2.followers.all()
        self.prof1.unfollow(self.user2)
        self.assertFalse(all_followers.exists())

    def test_unfollow_method_user_not_following(self):
        with self.assertRaisesMessage(ValidationError, 'You are not following this user.'):
            self.prof1.unfollow(self.user2)
            
    def test_total_followers_property(self):
        self.user2.profile.follow(self.prof1.user)
        count_followers = self.prof1.user.followers.all().count()
        self.assertEqual(self.prof1.total_followers, count_followers)
     
    def test_total_following_property(self):
        self.prof1.follow(self.user2)
        count_following = self.prof1.user.following.all().count()
        self.assertEqual(self.prof1.total_following, count_following)
        

class TestProfileLikeMethod(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post1 = PostFactory(author=self.user1)
    
    def test_like_post_method_succesfully(self):
        user2 = UserFactory()
        user2.profile.like_post(self.post1)
        self.assertEqual(self.post1.likes.all().count(), 1)
        
    def test_like_an_user_twice_fails(self):
        user2 = UserFactory()
        user2.profile.like_post(self.post1)
        with self.assertRaisesMessage(ValidationError, 'You have already liked this post.'):
            user2.profile.like_post(self.post1)



class TestFollow(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        
    def test_user_cannot_follow_themselves(self):
        with self.assertRaisesMessage(ValidationError, 'User cannot follow themselves.'):
            Follow.objects.create(
                follower=self.user1,
                followed=self.user1
            )