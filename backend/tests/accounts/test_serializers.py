from rest_framework.test import APITestCase, APIRequestFactory
from accounts.models import Profile, User, Follow
from tests.accounts.factories import UserFactory, FollowFactory
from accounts.serializers import (
    UserSerializer,ProfileSerializer, UserCreationSerializer, UserUpdateSerializer,
    FollowerSerializer, FollowedSerializer, FollowSerializer, ProfileSimpleSerializer
                                  )
from django.urls import reverse
from posts.models import Post


class TestUserSerializer(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        factory = APIRequestFactory()
        request = factory.get(reverse('user-detail', args=[self.user.id]))
        self.serializer = UserSerializer(
            self.user, context={'request': request})

    def test_data_serialized(self):
        expected = {
            'id': self.user.id,
            'username': self.user.username,
            'is_active': self.user.is_active
        }
        serialized_fields = {
            'id': self.serializer.data['id'],
            'username': self.serializer.data['username'],
            'is_active': self.serializer.data['is_active'],
        }
        self.assertDictEqual(serialized_fields, expected)

    def test_profile_detail_url_field_serialized(self):
        profile_detail_url = reverse(
            'profile-detail', args=[self.user.profile.id])
        self.assertEqual(self.serializer.data['profile_detail_url'].replace(
            'http://testserver', ''), profile_detail_url)


class TestUserCreationSerializer(APITestCase):
    def setUp(self) -> None:
        self.data = {
            'username': 'user00',
            'email': 'em@gmail.com',
            'password': 'senha123@',
        }
        
    def test_data_created_serialized(self):
        serializer = UserCreationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.assertEqual(serializer.data['username'], self.data['username'])
        self.assertEqual(serializer.data['email'], self.data['email'])
        user_qs = User.objects.filter(id=serializer.data['id'])
        self.assertTrue(user_qs.exists())
        user = user_qs.first()
        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(user.email, self.data['email'])
    
    def test_password_is_hashed(self):
        serializer = UserCreationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        user = User.objects.get(username=serializer.data['username'])
        self.assertTrue(user.check_password(self.data['password']))
        


class TestUserUpdateSerializer(APITestCase):
    def setUp(self) -> None:
        self.old_password = 'senhalegal123@'
        self.user = UserFactory(password=self.old_password)
    
    def test_data_updated_serialized(self):
        data = {
            'old_password': self.old_password,
            'password': 'senhanova123@',
            'username': 'username14'
        }
        serializer = UserUpdateSerializer(data=data, instance=self.user)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertTrue(self.user.check_password(data['password']))
        self.assertEqual(serializer.data['username'], data['username'])


class TestProfileSerializer(APITestCase):
    def setUp(self) -> None:
        user = UserFactory()
        self.profile = Profile.objects.get(user=user)
        factory = APIRequestFactory()
        request = factory.get(
            reverse('profile-detail', args=[self.profile.id]))
        self.serializer = ProfileSerializer(
            self.profile, context={'request': request})

    def test_id_name_bio_field_serialized(self):
        expected = {
            'id': self.profile.id,
            'name': self.profile.name,
            'bio': self.profile.bio,
        }
        serialized_fields = {
            'id': self.serializer.data['id'],
            'name': self.serializer.data['name'],
            'bio': self.serializer.data['bio'],
        }
        self.assertDictEqual(serialized_fields, expected)

    def test_created_at_field_serialized(self):
        expected = {
            'created_at': self.profile.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        }
        self.assertEqual(
            self.serializer.data['created_at'], expected['created_at'])

    def test_picture_field_serialized(self):
        expected = {
            'picture': self.profile.picture.url,
        }
        self.assertEqual(self.serializer.data['picture'].replace(
            'http://testserver', ''), expected['picture'])

    def test_user_nested_field_serialized(self):
        expected = {'user': {
            'id': self.profile.user.id,
            'username': self.profile.user.username,
            'is_active': self.profile.user.is_active,
            'profile_detail_url': reverse('profile-detail', args=[self.profile.id]),
        }, }
        self.serializer.data['user']['profile_detail_url'] = self.serializer.data['user']['profile_detail_url'].replace('http://testserver', '')
        self.assertEqual((self.serializer.data['user']), expected['user'])

    def test_total_posts_serialized(self):
        expected = {
            'total_posts': Post.objects.filter(author=self.profile.user).count()
        }
        self.assertEqual(
            self.serializer.data['total_posts'], expected['total_posts'])

    def test_total_followers_serialized(self):
        user = self.profile.user
        FollowFactory(followed=user)
        FollowFactory(followed=user)
        expected = {
            'total_followers': 2
        }
        self.assertEqual(
            self.serializer.data['total_followers'], expected['total_followers'])

    def test_total_following_serialized(self):
        user = self.profile.user
        FollowFactory(follower=user)
        FollowFactory(follower=user)
        expected = {
            'total_following': 2
        }
        self.assertEqual(
            self.serializer.data['total_following'], expected['total_following']
            )


class TestProfileSimpleSerializer(APITestCase):
    def setUp(self) -> None:
        user = UserFactory(username='Oreia')
        self.profile = user.profile
        self.profile.name = 'John Doe'
        self.profile.save()
        factory = APIRequestFactory()
        self.request = factory.get('/')
        
    def test_initial_data_returned(self):
        user_serialzed = UserSerializer(self.profile.user, context={'request': self.request}).data
        expected = {
            'id': self.profile.id,
            'name': self.profile.name,
            'picture': 'http://testserver'+self.profile.picture.url,
            'user': user_serialzed
        }
        serializer = ProfileSimpleSerializer(self.profile, context={'request': self.request})
        self.assertEqual(serializer.data['id'], expected['id'])
        self.assertEqual(serializer.data['name'], expected['name'])
        self.assertEqual(serializer.data['picture'], expected['picture'])
        self.assertEqual(serializer.data['user'], expected['user'])
        
        

class TestFollowSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        factory = APIRequestFactory()
        self.request = factory.get('/')
    
    def test_follow_user_successfully(self):
        self.request.user = self.user1
        data = {
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        follow = Follow.objects.filter(followed=data['followed'], follower=self.request.user)
        self.assertTrue(follow.exists())
        
    def test_follow_user_already_followed_fails(self):
        self.request.user = self.user1
        data = {
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        data = {
            'followed': self.user2.id,
        }
        serializer = FollowSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        expected = {
            'detail': 'You are already following this user.'
        }
        self.assertEqual(str(serializer.errors['detail'][0]), expected['detail'])
        
    def test_follow_yourself_fails(self):
        self.request.user = self.user1
        data = {
            'followed': self.user1.id,
        }
        serializer = FollowSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
        expected = {
            'detail': 'You can not follow yourself.'
        }
        self.assertEqual(str(serializer.errors['detail'][0]), expected['detail'])

    def test_follow_that_does_not_exist_fails(self):
        self.request.user = self.user1
        data = {
            'followed': 999,
        }
        serializer = FollowSerializer(data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())



class TestFollowerSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.all_followers = []
        for c in range(3):
            self.all_followers.append(FollowFactory(followed=self.user1))
        
    def test_return_all_serilized_followers_users(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        serializer = FollowerSerializer(self.all_followers, many=True, context={'request': request})
        expected = []
        for follow in self.all_followers:
            data = {'profile': ProfileSimpleSerializer(follow.follower.profile, context={'request': request}).data, 'created_at': follow.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
            expected.append(data)
        self.assertEqual(serializer.data[0]['profile'], expected[0]['profile'])
        

class TestFollowedSerializer(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.all_following = []
        for c in range(3):
            self.all_following.append(FollowFactory(follower=self.user1))
        
    def test_return_all_serilized_following_users(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        serializer = FollowedSerializer(self.all_following, many=True, context={'request': request})
        expected = []
        for follow in self.all_following:
            data = {'profile': ProfileSimpleSerializer(follow.followed.profile, context={'request': request}).data, 'created_at': follow.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
            expected.append(data)
        self.assertEqual(serializer.data[0]['profile'], expected[0]['profile'])
        
        
