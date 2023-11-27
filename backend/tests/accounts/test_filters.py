from rest_framework.test import APITestCase    
from rest_framework import status
from tests.accounts.factories import UserFactory, FollowFactory
from django.urls import reverse
from datetime import datetime, timedelta


class TestUserFilter(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory(username='John Doe', is_active=False)
        self.user2 = UserFactory(username='Jane Doe', is_active=True)
        self.endoint_using_the_filter = reverse('user-list')
    
    def test_is_active_filter_field(self):
        params = {'is_active': True}
        response = self.client.get(self.endoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')
        
    def test_username_filter_field(self):        
        params = {'username': 'John'}
        response = self.client.get(self.endoint_using_the_filter, params)
                
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Jane Doe')


class TestProfileFilter(APITestCase):
    def setUp(self) -> None:
        user1 = UserFactory(username='Paul 1')
        self.profile1 = user1.profile
        self.profile1.name = 'John Doe'
        self.profile1.bio = 'Lorem ipsum more'

        user2 = UserFactory(username='Paul 2')
        self.profile2 = user2.profile
        self.profile2.name = 'Jane Doe'
        self.profile2.bio = 'Lorem ipsum less'
        
        self.profile1.save()
        self.profile2.save()
        self.endoint_using_the_filter = reverse('profile-list')

    def test_search_field_filtering_by_name(self):
        params = {'search': 'Jane'}
        response = self.client.get(self.endoint_using_the_filter, params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')

    def test_search_field_filtering_by_bio(self):
        params = {'search': 'les'}
        response = self.client.get(self.endoint_using_the_filter, params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')

    def test_search_field_filtering_by_username(self):
        params = {'search': '1'}
        response = self.client.get(self.endoint_using_the_filter, params)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paul 1')
        self.assertNotContains(response, 'Jane Doe')
        self.assertNotContains(response, 'Paul 2')


class TestFollowerFilter(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.follower1 = FollowFactory(followed=self.user).follower
        self.follower1.profile.name = 'John Doe' 
        self.follower1.username = 'Paul 12'
        
        self.follower2 = FollowFactory(followed=self.user).follower
        self.follower2.profile.name = 'Jane Doe'
        self.follower2.username = 'Paul 13'
        
        self.follower1.save()
        self.follower2.save()
        self.follower1.profile.save()
        self.follower2.profile.save()
        
        self.endoint_using_the_filter = reverse('follower-list', args=[self.user.id])
                
    def test_search_field_filtering_by_profile_name(self):
        params = {'search': 'Jane'}
        response = self.client.get(self.endoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')
        self.assertNotContains(response, 'Paul 12')
        
    def test_search_field_filtering_by_username(self):
        params = {'search': '12'}
        response = self.client.get(self.endoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paul 12')
        self.assertNotContains(response, 'Jane Doe')
        self.assertNotContains(response, 'Paul 13')

    def test_created_at_field_filter(self):
        follow1 = self.follower1.following.get(followed=self.user)
        follow1.created_at = datetime(year=2023, month=9, day=10) 
        follow1.save()
        follow2 = self.follower2.following.get(followed=self.user)
        follow2.created_at = datetime(year=2023, month=10, day=10)
        follow2.save()
        
        params = {'created_at_after': '2023-10-09', 'created_at_before': '2023-10-11'}
        response = self.client.get(self.endoint_using_the_filter, params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')
        

class TestFollowedFilter(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.followed1 = FollowFactory(follower=self.user).followed
        self.followed1.profile.name = 'John Doe' 
        self.followed1.username = 'Paul 12'
        
        self.followed2 = FollowFactory(follower=self.user).followed
        self.followed2.profile.name = 'Jane Doe'
        self.followed2.username = 'Paul 13'
        
        self.followed1.save()
        self.followed2.save()
        self.followed1.profile.save()
        self.followed2.profile.save()
        
        self.endoint_using_the_filter = reverse('followed-list', args=[self.user.id])
                
    def test_search_field_filtering_by_profile_name(self):
        params = {'search': 'Jane'}
        response = self.client.get(self.endoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')
        self.assertNotContains(response, 'Paul 12')
        
    def test_search_field_filtering_by_username(self):
        params = {'search': '12'}
        response = self.client.get(self.endoint_using_the_filter, params)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paul 12')
        self.assertNotContains(response, 'Jane Doe')
        self.assertNotContains(response, 'Paul 13')

    def test_created_at_field_filter(self):
        follow1 = self.followed1.followers.get(follower=self.user)
        follow1.created_at = datetime(year=2023, month=9, day=10) 
        follow1.save()
        follow2 = self.followed2.followers.get(follower=self.user)
        follow2.created_at = datetime(year=2023, month=10, day=10)
        follow2.save()
        
        params = {'created_at_after': '2023-10-09', 'created_at_before': '2023-10-11'}
        response = self.client.get(self.endoint_using_the_filter, params)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Doe')
        self.assertNotContains(response, 'John Doe')
