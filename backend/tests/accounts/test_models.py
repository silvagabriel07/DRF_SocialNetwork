from django.test import TestCase
from accounts.models import User, Profile
from tests.factories import UserFactory

class TestProfile(TestCase):
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
        self.assertTrue(self.prof1.follow(self.user2))
        all_following = self.prof1.user.following.all()
        self.assertEqual(all_following.count(), 1)
        self.assertEqual(all_following.first().followed, self.user2)
        all_followers = self.prof1.user.followers.all()
        self.assertFalse(all_followers.exists())
        
    def test_follow_method_users_followers(self):
        self.assertTrue(self.prof1.follow(self.user2))
        all_followers = self.user2.followers.all()
        self.assertEqual(all_followers.count(), 1)
        self.assertEqual(all_followers.first().follower.profile, self.prof1)
        all_following = self.user2.following.all()
        self.assertFalse(all_following.exists())
        
    def test_follow_method_self_following_fails(self):
        self.assertFalse(self.prof1.follow(self.prof1.user))

    def test_follow_method_user_followed_twice_by_the_same_user(self):
        self.assertTrue(self.prof1.follow(self.user2))
        self.assertFalse(self.prof1.follow(self.user2))    
    
    def test_unfollow_method_user_following(self):
        self.assertTrue(self.prof1.follow(self.user2))
        all_followers = self.user2.followers.all()
        self.prof1.unfollow(self.user2)
        self.assertFalse(all_followers.exists())

    def test_unfollow_method_user_not_following(self):
        self.assertFalse(self.prof1.unfollow(self.user2))

    def test_followers_property(self):
        self.user2.profile.follow(self.prof1)
        all_followers = self.prof1.user.followers.all()
        self.assertEqual(list(self.prof1.followers), list(all_followers))
     
    def test_following_property(self):
        self.prof1.follow(self.user2)
        all_following = self.prof1.user.following.all()
        self.assertEqual(list(self.prof1.following), list(all_following))
        
