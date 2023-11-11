from rest_framework.test import APITestCase, APIRequestFactory
from accounts.models import Profile
from tests.factories import UserFactory
from accounts.serializers import UserSerializer, ProfileSerializer
from django.urls import reverse

class TestUserSerializer(APITestCase):    
    def setUp(self) -> None:
        self.user = UserFactory()
        factory = APIRequestFactory()
        request = factory.get(reverse('user-detail', args=[self.user.id]))
        self.serializer = UserSerializer(self.user, context={'request': request})

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
        profile_detail_url = reverse('profile-detail', args=[self.user.profile.id])
        self.assertEqual(self.serializer.data['profile_detail_url'].replace('http://testserver', ''), profile_detail_url)


class TestProfileSerializer(APITestCase):
    def setUp(self) -> None:
        user = UserFactory()
        self.profile = Profile.objects.get(user=user)
        factory = APIRequestFactory()
        request = factory.get(reverse('profile-detail', args=[self.profile.id]))
        self.serializer = ProfileSerializer(self.profile, context={'request': request})

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
        self.assertEqual(self.serializer.data['created_at'], expected['created_at'])
        
    def test_picture_field_serialized(self):
        expected = {
            'picture': self.profile.picture.url,
        }
        self.assertEqual(self.serializer.data['picture'].replace('http://testserver', ''), expected['picture'])
        
    def test_user_detail_url_field_serialized(self):
        expected = {
            'user_detail_url': reverse('user-detail', args=[self.profile.user.id]),
        }
        self.assertEqual(self.serializer.data['user_detail_url'].replace('http://testserver', ''), expected['user_detail_url'])

