from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import Profile, User
from tests.accounts.factories import UserFactory
from accounts.serializers import UserSerializer, ProfileSerializer
from django.urls import reverse
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile

class TestUserDetail(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.url = reverse('user-detail', args=[self.user.id])
    
    def test_data_returned(self):
        response = self.client.get(self.url)
        serializer = UserSerializer(self.user, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
        
class TestUserRegistration(APITestCase):
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
            'id': response.data['id'],
            'username': data['username'],
            'email': data['email'],
            'is_active': response.data['is_active'],
        }
        self.assertEqual(response.data, expected)
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

        
class TestUserList(APITestCase):
    def setUp(self) -> None:
        self.users = UserFactory.create_batch(3)
        self.url = reverse('user-list')
        
    def test_get_list_user(self):
        response = self.client.get(self.url)
        users = User.objects.all()
        serializer = UserSerializer(users, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestUserUpdate(APITestCase):
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
            'password': 'coolpass0@'
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


class TestUserDelete(APITestCase):
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
        

class TestProfileDetail(APITestCase):
    def setUp(self) -> None:
        user = UserFactory()
        self.profile = Profile.objects.get(user=user)
        self.url = reverse('profile-detail', args=[self.profile.id])
    
    def test_data_returned(self):
        response = self.client.get(self.url)
        serializer = ProfileSerializer(self.profile, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestProfileList(APITestCase):
    def setUp(self) -> None:
        UserFactory.create_batch(3)
        self.url = reverse('profile-list')
    
    def test_data_listed_returned(self):
        response = self.client.get(self.url)
        all_profiles = Profile.objects.all() 
        serializer = ProfileSerializer(all_profiles, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestProfileUpdate(APITestCase):
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
        

