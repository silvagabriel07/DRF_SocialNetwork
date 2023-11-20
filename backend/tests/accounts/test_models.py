from rest_framework.test import APITestCase 
from accounts.models import User, Profile, Follow
from tests.accounts.factories import UserFactory
from tests.posts.factories import PostFactory, TagFactory, PostLikeFactory, CommentFactory, CommentLikeFactory
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError

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
        with self.assertRaisesMessage(ValidationError, 'You can not follow yourself.'):
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
        with self.assertRaisesMessage(ValidationError, 'You were not following this user.'):
            self.prof1.unfollow(self.user2)
            
    def test_total_followers_property(self):
        self.user2.profile.follow(self.prof1.user)
        count_followers = self.prof1.user.followers.all().count()
        self.assertEqual(self.prof1.total_followers, count_followers)
     
    def test_total_following_property(self):
        self.prof1.follow(self.user2)
        count_following = self.prof1.user.following.all().count()
        self.assertEqual(self.prof1.total_following, count_following)
        

class TestProfilePostMethods(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.post1 = PostFactory(author=self.user1)
    
    def test_like_post_method_successfully(self):
        self.user2.profile.like_post(self.post1)
        self.assertEqual(self.post1.likes.all().count(), 1)
        
    def test_like_post_twice_fails(self):
        self.user2.profile.like_post(self.post1)
        with self.assertRaisesMessage(ValidationError, 'You have already liked this post.'):
            self.user2.profile.like_post(self.post1)

    def test_dislike_a_post_successfully(self):
        PostLikeFactory(post=self.post1, user=self.user2)
        self.assertEqual(self.post1.likes.all().count(), 1)
        self.user2.profile.dislike_post(self.post1)
        self.assertEqual(self.post1.likes.all().count(), 0)
        
    def test_dislike_a_post_that_user_did_not_like_fails(self):
        with self.assertRaisesMessage(ValidationError, 'You were not liking this post.'):
            self.user2.profile.dislike_post(self.post1)
    
    def test_return_total_posts(self):
        PostFactory(author=self.user1)
        count_posts = self.user1.posts.all().count()
        self.assertEqual(self.user1.profile.total_posts, count_posts)


class TestProfileCommentMethods(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.comment1 = CommentFactory(author=self.user1)

    def test_like_comment_method_successfully(self):
        self.user2.profile.like_comment(self.comment1)
        self.assertEqual(self.comment1.likes.all().count(), 1)
        
    def test_like_comment_twice_fails(self):
        self.user2.profile.like_comment(self.comment1)
        with self.assertRaisesMessage(ValidationError, 'You have already liked this comment.'):
            self.user2.profile.like_comment(self.comment1)

    def test_dislike_a_comment_successfully(self):
        CommentLikeFactory(comment=self.comment1, user=self.user2)
        self.assertEqual(self.comment1.likes.all().count(), 1)
        self.user2.profile.dislike_comment(self.comment1)
        self.assertEqual(self.comment1.likes.all().count(), 0)
        
    def test_dislike_a_comment_that_user_did_not_like_fails(self):
        with self.assertRaisesMessage(ValidationError, 'You did not like this comment.'):
            self.user2.profile.dislike_comment(self.comment1)


class TestFollow(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        
    def test_user_cannot_follow_themselves(self):
        with self.assertRaisesMessage(ValidationError, 'You can not follow yourself.'):
            Follow.objects.create(
                follower=self.user1,
                followed=self.user1
            )