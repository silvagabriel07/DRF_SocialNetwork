from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Profile, User
from tests.accounts.factories import UserFactory, FollowFactory
from accounts.serializers import UserSerializer, ProfileSerializer, ProfileSimpleSerializer, UserCreationSerializer, FollowedSerializer, FollowerSerializer
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
                'username': data['username'],
                'email': data['email'],
                },
        }
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], expected['user']['username'])
        self.assertEqual(response.data['user']['email'], expected['user']['email'])
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
        
    def test_update_password_with_invalid_old_password(self):
        data = {
            'old_password': 'WRONGpassword123@',
            'password': 'coolpass0@',
            'username': 'user00'
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, data['username'])
        self.assertFalse(self.user.check_password(data['password']))
        
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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(username=data['username']).exists())
        self.assertEqual(response.data['detail'], 'You are not authorized to perform this action.')


class TestUserDeleteView(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse('user-delete', args=[self.user.id])
    
    def test_delete_user_successfully(self):
        self.client.force_login(self.user) 
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 0)

    def test_delete_user_is_not_deleted_if_is_not_the_user_from_the_request(self):
        user2 = UserFactory()
        self.client.force_login(user2)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(User.objects.all().count(), 2)
        self.assertIn('You are not authorized to perform this action.', response.data['detail'])
        

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
        response = self.client.patch(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['bio'], data['bio'])
        self.assertTrue(Profile.objects.filter(bio=data['bio'], name=data['name']).exists())
    
    def test_put_profile_is_not_updated_if_the_profile_user_is_not_the_user_from_the_request(self):
        user2 = UserFactory()
        self.client.logout()
        self.client.force_login(user2)
        data = {
            'name': 'user00099',
        }
        response = self.client.put(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Profile.objects.filter(name=data['name']).exists())
        self.assertEqual('You are not authorized to perform this action.', response.data['detail'])
        self.assertFalse(Profile.objects.filter(name=data['name']).exists())

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_patch_update_picture(self):
        data = {
            'name': 'user updated pic',
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
        self.assertTrue(Profile.objects.filter(name=data['name']).exists())
    
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
        response = self.client.patch(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Profile.objects.filter(name=data['name']).exists())


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
        self.assertEqual(str(response.data['detail'][0]), expected['detail'])
        self.assertEqual(self.user1.following.all().count(), 1)
        
    def test_follow_yourself_fails(self):
        url = reverse('follow-user', args=[self.user1.id])
        response = self.client.post(url)
        expected = {
            'detail': 'You can not follow yourself.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertContains(response, expected['detail'], status_code=400)
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
            follow_serialized = FollowerSerializer(instance=follow, context={'request': response.wsgi_request})
            expected.append(follow_serialized.data)
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
            follow_serialized = FollowedSerializer(instance=follow, context={'request': response.wsgi_request})
            expected.append(follow_serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], expected)
        
        
