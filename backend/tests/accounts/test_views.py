from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Profile, User
from tests.accounts.factories import UserFactory, FollowFactory
from accounts.serializers import UserSerializer, ProfileSerializer, ProfileSimpleSerializer
from django.urls import reverse
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

class TestUserDetailView(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse('user-detail', args=[self.user.id])
    
    def test_data_returned(self):
        response = self.client.get(self.url)
        serializer = UserSerializer(self.user, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
        
class TestUserRegistrationView(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('user-registration')
        self.user = UserFactory()
    
    def test_post_create_user_successfully(self):
        data = {
            'username': 'user00',
            'email': 'email00@gmail.com',
            'password': 'pessoas00@',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = {
            'user': {
                'id': response.data['user']['id'],
                'username': data['username'],
                'email': data['email'],
                'is_active': response.data['user']['is_active']
                },
        }
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user'], expected['user'])
        self.assertTrue(User.objects.filter(email=data['email'], username=data['username']).exists())

    def test_post_with_already_existing_username_fails(self):
        data = {
            'username': self.user.username,
            'email': 'email00@gmail.com',
            'password': 'pessoas00@',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_with_already_existing_email_fails(self):
        data = {
            'username': 'user00',
            'email': self.user.email,
            'password': 'pessoas00@',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_post_password_with_less_than_8_characters(self):
        data = {
            'username': 'user00',
            'email': 'email00@gmail.com',
            'password': 'pessoa1',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is too short. It must contain at least 8 characters.', response.data['password'])        
        
    def test_post_password_with_only_numbers(self):
        data = {
            'username': 'user00',
            'email': 'email00@gmail.com',
            'password': '00123456',
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This password is entirely numeric.', response.data['password'])        

        
class TestUserListView(APITestCase):
    def setUp(self) -> None:
        self.users = UserFactory.create_batch(3)
        self.url = reverse('user-list')
        
    def test_get_list_user(self):
        response = self.client.get(self.url)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)


class TestUserUpdateView(APITestCase):
    def setUp(self) -> None:
        self.user_old_password = 'Testado123@'
        self.user = UserFactory(password=self.user_old_password)
        self.url = reverse('user-update', args=[self.user.id])
        self.client.force_login(self.user)
        
    def test_patch_update_username(self):
        data = {
            'old_password': self.user_old_password,
            'username': 'user00'
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username=data['username']).exists())

    def test_patch_update_password(self):
        data = {
            'old_password': self.user_old_password,
            'password': 'coolpass0@',
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(data['password']))

    def test_put_update_password_and_username(self):
        data = {
            'old_password': self.user_old_password,
            'password': 'coolpass0@',
            'username': 'user00'
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data['username'])
        self.assertTrue(self.user.check_password(data['password']))
        
    def test_put_user_is_not_updated_if_is_not_the_user_from_the_request(self):
        user2 = UserFactory()
        self.client.logout()
        self.client.force_login(user2)
        data = {
            'old_password': self.user_old_password,
            'username': 'user00',
            'password': 'coolpass0@',
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(User.objects.filter(username=data['username']).exists())
        self.assertIn('You are not authorized to perform this action.', response.data['request.user'])


class TestUserDeleteView(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse('user-delete', args=[self.user.id])
    
    def test_delete_user_successfully(self):
        self.client.force_login(self.user) 
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 0)

    def test_delete_user_is_not_updated_if_is_not_the_user_from_the_request(self):
            user2 = UserFactory()
            self.client.force_login(user2)
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(User.objects.all().count(), 2)
            self.assertIn('You are not authorized to perform this action.', response.data['request.user'])
        

class TestProfileDetailView(APITestCase):
    def setUp(self) -> None:
        user = UserFactory()
        self.profile = Profile.objects.get(user=user)
        self.url = reverse('profile-detail', args=[self.profile.id])
    
    def test_data_returned(self):
        response = self.client.get(self.url)
        serializer = ProfileSerializer(self.profile, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestProfileListView(APITestCase):
    def setUp(self) -> None:
        UserFactory.create_batch(3)
        self.url = reverse('profile-list')
    
    def test_data_listed_returned(self):
        response = self.client.get(self.url)
        all_profiles = Profile.objects.all() 
        serializer = ProfileSerializer(all_profiles, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)


class TestProfileUpdateView(APITestCase):
    def setUp(self) -> None:
        user = UserFactory()
        self.client.force_login(user)
        self.profile = Profile.objects.get(user=user)
        self.url = reverse('profile-update', args=[self.profile.id])
        
    def test_patch_update_name_and_bio(self):
        data = {
            'name': 'newname',
            'bio': 'new bio sla.',
        }
        expected = {
            'name': data['name'],
            'bio': data['bio'],
            'picture': self.profile.picture.url.replace('http://testserver', ''),
        }
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], expected['name'])
        self.assertEqual(response.data['bio'], expected['bio'])
        self.assertEqual(response.data['picture'].replace(
            'http://testserver', ''), expected['picture'])
        

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_patch_update_picture(self):
        data = {
            'picture': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        }
        expected = {
            'picture': data['picture'].name,
        }
        response = self.client.patch(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['picture'].split('/')[-1], expected['picture'])
        self.profile.refresh_from_db()
        self.assertEqual((self.profile.picture.name).split('/')[-1], expected['picture'])
    
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_put_update_profile_must_belong_to_requesting_user(self):
        self.client.logout()
        another_user = UserFactory()
        self.client.force_login(another_user)
        data = {
            'name': 'newname',
            'bio': 'new bio sla.',
            'picture': SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
        }
        expected = {
            'name': data['name'],
            'bio': data['bio'],
            'picture': data['picture'].name,
        }
        response = self.client.patch(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class TestFollowUserView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.client.force_login(self.user1)
    
    def test_follow_user_successfully(self):
        url = reverse('follow-user', args=[self.user2.id])
        response = self.client.post(url)
        expected = {
            'message': 'You have successfully followed the user.'        
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.following.all().count(), 1)
    
    def test_follow_user_with_pk_of_a_non_existing_user_fails(self):
        invalid_pk = 10
        url = reverse('follow-user', args=[invalid_pk])
        response = self.client.post(url)
        expected = {
            'detail': 'The user does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.following.all().count(), 0)
    
    def test_follow_user_already_followed_fails(self):
        FollowFactory(follower=self.user1, followed=self.user2)
        url = reverse('follow-user', args=[self.user2.id])
        response = self.client.post(url)
        expected = {
            'detail': 'You are already following this user.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)
        self.assertEqual(self.user1.following.all().count(), 1)
        
    def test_follow_yourself_fails(self):
        url = reverse('follow-user', args=[self.user1.id])
        response = self.client.post(url)
        expected = {
            'detail': 'You can not follow yourself.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)
        self.assertEqual(self.user1.following.all().count(), 0)


class TestUnfollowUserView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.client.force_login(self.user1)
    
    def test_unfollow_user_successfully(self):
        FollowFactory(follower=self.user1, followed=self.user2)
        url = reverse('unfollow-user', args=[self.user2.id])
        response = self.client.delete(url)
        expected = {
            'message': 'You have successfully unfollowed the user.'        
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.following.all().count(), 0)
    
    def test_unfollow_user_with_pk_of_a_non_existing_user_fails(self):
        invalid_pk = 10
        url = reverse('unfollow-user', args=[invalid_pk])
        response = self.client.delete(url)
        expected = {
            'detail': 'The user does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.following.all().count(), 0)
    
    def test_unfollow_user_that_is_not_followed_fails(self):
        url = reverse('unfollow-user', args=[self.user2.id])
        response = self.client.delete(url)
        expected = {
            'detail': 'You were not following this user.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)
        self.assertEqual(self.user1.following.all().count(), 0)
        

class TestFollowerListView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.all_followers = []
        for follow in range(3):
            self.all_followers.append(FollowFactory(followed=self.user1))
        self.client.force_login(self.user1)
    
    def test_list_all_followers_users_of_a_user(self):
        response = self.client.get(reverse('follower-list', args=[self.user1.id]))
        expected = []
        for follow in self.all_followers:
            data = {'profile': ProfileSimpleSerializer(follow.follower.profile, context={'request': response.wsgi_request}).data, 'created_at': follow.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
            expected.append(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], expected)

class TestFollowedListView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.all_following = []
        for follow in range(3):
            self.all_following.append(FollowFactory(follower=self.user1))
        self.client.force_login(self.user1)
    
    def test_list_all_followed_users_of_a_user(self):
        response = self.client.get(reverse('followed-list', args=[self.user1.id]))
        expected = []
        for follow in self.all_following:
            data = {'profile': ProfileSimpleSerializer(follow.followed.profile, context={'request': response.wsgi_request}).data, 'created_at': follow.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}
            expected.append(data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], expected)
        
        
