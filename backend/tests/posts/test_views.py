from rest_framework.test import APITestCase, APIRequestFactory
from tests.posts.factories import PostFactory, TagFactory, PostLikeFactory, CommentFactory, CommentLikeFactory
from tests.accounts.factories import UserFactory, FollowFactory

from posts.models import Post, Tag, Comment
from posts.serializers import PostSerializer, TagSerializer, CommentSerializer, CommentLikeSerializer, PostLikeSerializer, ProfileSimpleSerializer
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from unittest.mock import patch


class TestPostListCreateView(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('post-list-create')
        self.user1 = UserFactory()
        self.client.force_login(self.user1)

        self.tags = TagFactory.create_batch(3)
       
    def test_list_all_nested_tags_in_post(self):
        post = PostFactory()
        post.tags.set(self.tags)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = [{'id': tag.id, 'name': tag.name}
                    for tag in post.tags.all()]
        ordered_nested_tags = [ordered_post['nested_tags']
                               for ordered_post in response.data['results']]
        response_nested_tags_data = [
            {'id': tag['id'], 'name': tag['name']} for tag in ordered_nested_tags[0]]
        self.assertListEqual(response_nested_tags_data, expected)

    def test_list_all_posts(self):
        PostFactory.create_batch(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PostSerializer(Post.objects.all(), many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_post_with_more_than_30_tags_fails(self):
        data = {
            'title': 'title 1',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'tags': [tag.id for tag in TagFactory.create_batch(31)],
        }
        response = self.client.post(self.url, data=data, format='json')
        expected = {'tags':
                    {'detail': "A post can't have more than 30 tags."}
                    }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)

    def test_create_post_successfully(self):
        data = {
            'title': 'title 1',
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
            'tags': [self.tags[0].id, self.tags[1].id, self.tags[2].id, ],
        }
        response = self.client.post(self.url, data=data, format='json')
        response.data.pop('nested_tags')
        expected = {
            'id': response.data['id'],
            'title': data['title'],
            'content': data['content'],
            'author': ProfileSimpleSerializer(self.user1.profile, context={'request': response.wsgi_request}).data,
            #    'nested_tags': data['tags'],     We already test this field separetely.
            'created_at': response.data['created_at'],
            'total_likes': 0,
            'total_tags': len(data['tags']),
            'total_comments': 0,
            'edited': response.data['edited']
        }

        self.assertEqual(response.data, expected)
        post_created = Post.objects.get(id=expected['id'])
        self.assertEqual(
            [tag.id for tag in post_created.tags.all()], data['tags'])


class TestPostFeedView(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('post-list-create')
        self.user1 = UserFactory()
        self.client.force_login(self.user1)
        
        self.followed_user = FollowFactory(follower=self.user1).followed
        self.another_user = UserFactory()
    
    def test_list_all_posts_from_followed_users(self):
        post1 = PostFactory(author=self.followed_user)
        post2 = PostFactory(author=self.another_user)
        
        response = self.client.get(reverse('post-feed-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0], PostSerializer(post1, context={'request': response.wsgi_request}).data)


class TestPostDetailView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.client.force_login(self.user1)
        self.url = reverse('post-detail', args=[self.user1.id])

        self.tags = TagFactory.create_batch(3)
    def test_return_data(self):
        post = PostFactory()
        response = self.client.get(self.url)
        serializer = PostSerializer(post, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestPostUpdateView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory(author=self.user1)
        self.client.force_login(self.user1)
        self.url = reverse('post-update', args=[self.post.id])

    def test_patch_title_updated(self):
        data = {
            'title': 'Title updated'
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, data['title'])

    def test_patch_content_updated(self):
        data = {
            'content': 'Content updated'
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], data['content'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, data['content'])

    def test_patch_tags_updated(self):
        all_tags = TagFactory.create_batch(3)
        tags = [tag.id for tag in all_tags]
        data = {
            'tags': tags
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nested_tags'], [
                         {'id': tag.id, 'name': tag.name} for tag in all_tags])
        self.post.refresh_from_db()
        self.assertEqual(list(self.post.tags.all()), all_tags)

    def test_put_return_data(self):
        all_tags = TagFactory.create_batch(3)
        tags = [tag.id for tag in all_tags]
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
            'tags': tags
        }
        response = self.client.put(self.url, data=data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['nested_tags'], [{'id': tag.id, 'name': tag.name} for tag in all_tags])

    def test_update_post_user_of_the_request_must_be_the_owner(self):
        another_user = UserFactory()
        self.client.logout()
        self.client.force_login(another_user)
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
        }
        response = self.client.patch(self.url, data=data)
        expected = {
            'detail': 'You are not authorized to perform this action.'
        }
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, expected)
        
    def test_put_update_post_with_more_than_30_tags_fails(self):
        all_tags = TagFactory.create_batch(31)
        tags = [tag.id for tag in all_tags]
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
            'tags': tags
        }
        response = self.client.put(self.url, data=data)
        expected = {'tags':
                    {'detail': "A post can't have more than 30 tags."}
                    }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)
    
    @patch('posts.mixins.timezone')
    def test_patch_update_post_after_12_hours_fails(self, mock_timezone):
        mock_timezone.now.return_value = timezone.now() + timezone.timedelta(days=1)
        mock_timezone.timedelta.return_value = timezone.timedelta(hours=12)
        data = {
            'title': 'Title updated',
            'content': 'Content updated',
        }
        response = self.client.patch(self.url, data=data)
        expected = {
                'detail': ['This post cannot be edited any further.']
            }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)


class TestPostDeleteView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.another_user = UserFactory()
        self.post = PostFactory(author=self.user1)
        self.url = reverse('post-delete', args=[self.post.id])

    def test_delete_post_user_of_the_request_must_be_the_owner(self):
        self.client.force_login(self.another_user)
        response = self.client.delete(self.url)
        expected = {
            'detail': 'You are not authorized to perform this action.'
        }
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, expected)

    def test_delete_post_successfully(self):
        self.client.force_login(self.user1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.all().exists())


class TestPostLikeListView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory(author=self.user1)
        self.client.force_login(self.user1)
        self.url = reverse('post-like-list', args=[self.post.id])
    def test_list_all_post_likes(self):
        all_postlikes = []
        for c in range(3):
            all_postlikes.append(PostLikeFactory(post=self.post))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PostLikeSerializer(all_postlikes, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.data['results'], serializer.data)


class TestLikePostView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.post = PostFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('like-post', args=[self.post.id])

    def test_like_post_successfully(self):
        response = self.client.post(self.url)
        expected = {
            'message': 'You have successfully liked the post.'
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.all().count(), 1)

    def test_like_post_already_liked_fails(self):
        PostLikeFactory(post=self.post, user=self.user1)
        response = self.client.post(self.url)
        expected = {
            'detail': 'You are already liking this post.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['detail'][0]), expected['detail'])
        self.assertEqual(self.post.likes.all().count(), 1)

    def test_like_post_with_pk_of_a_non_existing_post_fails(self):
        invalid_pk = 10
        url = reverse('like-post', args=[invalid_pk])
        response = self.client.post(url)
        expected = {
            'detail': 'The post does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)


class TestDislikePostView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.post = PostFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('dislike-post', args=[self.post.id])

    def test_dislike_post_successfully(self):
        PostLikeFactory(user=self.user1, post=self.post)
        response = self.client.delete(self.url)
        expected = {
            'message': 'You have successfully disliked the post.'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes.all().count(), 0)

    def test_dislike_post_that_is_not_liked_fails(self):
        response = self.client.delete(self.url)
        expected = {
            'detail': 'You were not liking this post.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)

    def test_dislike_post_with_pk_of_a_non_existing_post_fails(self):
        invalid_pk = 10
        url = reverse('dislike-post', args=[invalid_pk])
        response = self.client.delete(url)
        expected = {
            'detail': 'The post does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)


class TestTagListView(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('tag-list')

    def test_list_all_tags(self):
        TagFactory.create_batch(3)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = TagSerializer(Tag.objects.all(), many=True)
        self.assertEqual(response.data['results'], serializer.data)


class TestCommentListCreateView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.post = PostFactory()
        self.url = reverse('comment-list-create', args=[self.post.id])
        self.client.force_login(self.user1)
    def test_list_all_comments(self):
        all_tags = []
        for c in range(3):
            all_tags.append(CommentFactory(post=self.post))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CommentSerializer(all_tags, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_comment_successfully(self):
        data = {
            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        }
        response = self.client.post(self.url, data=data)
        expected = {
            'id': response.data['id'],
            'content': data['content'],
            'post': self.post.id,
            'author': ProfileSimpleSerializer(self.user1.profile, context={'request': response.wsgi_request}).data,
            'created_at': response.data['created_at'],
            'total_likes': 0,
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)


class TestCommentDetailView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.client.force_login(self.user1)
        self.post = PostFactory()
        self.comment = CommentFactory(post=self.post, author=self.user1)
        self.url = reverse('comment-detail', args=[self.post.id])
    def test_return_data(self):
        response = self.client.get(self.url)
        serializer = CommentSerializer(self.comment, context={'request': response.wsgi_request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class TestCommentDeleteView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.another_user = UserFactory()
        self.post = PostFactory()
        self.comment = CommentFactory(post=self.post, author=self.user1)
        self.url = reverse('comment-delete', args=[self.comment.id])

    def test_delete_comment_user_of_the_request_must_be_the_owner(self):
        self.client.force_login(self.another_user)
        response = self.client.delete(self.url)
        expected = {
            'detail': 'You are not authorized to perform this action.'
        }
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, expected)

    def test_delete_comment_successfully(self):
        self.client.force_login(self.user1)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.all().exists())


class TestLikeCommentView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.comment = CommentFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('like-comment', args=[self.comment.id])

    def test_like_comment_successfully(self):
        response = self.client.post(self.url)
        expected = {
            'message': 'You have successfully liked the comment.'
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, expected)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes.all().count(), 1)

    def test_like_comment_already_liked_fails(self):
        CommentLikeFactory(comment=self.comment, user=self.user1)
        response = self.client.post(self.url)
        expected = {
            'detail': 'You are already liking this comment.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['detail'][0]), expected['detail'])
        self.assertEqual(self.comment.likes.all().count(), 1)

    def test_like_comment_with_pk_of_a_non_existing_comment_fails(self):
        invalid_pk = 10
        url = reverse('like-comment', args=[invalid_pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.comment.likes.all().count(), 0)

class TestDislikecommentView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.comment = CommentFactory(author=self.user2)
        self.client.force_login(self.user1)
        self.url = reverse('dislike-comment', args=[self.comment.id])

    def test_dislike_comment_successfully(self):
        CommentLikeFactory(user=self.user1, comment=self.comment)
        response = self.client.delete(self.url)
        expected = {
            'message': 'You have successfully disliked the comment.'
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.likes.all().count(), 0)

    def test_dislike_comment_that_is_not_liked_fails(self):
        response = self.client.delete(self.url)
        expected = {
            'detail': 'You were not liking this comment.'
        }
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, expected)

    def test_dislike_comment_with_pk_of_a_non_existing_comment_fails(self):
        invalid_pk = 10
        url = reverse('dislike-comment', args=[invalid_pk])
        response = self.client.delete(url)
        expected = {
            'detail': 'The comment does not exist.'
        }
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, expected)


class TestCommentLikeListView(APITestCase):
    def setUp(self) -> None:
        self.user1 = UserFactory()
        self.comment = CommentFactory(author=self.user1)
        self.client.force_login(self.user1)
        self.url = reverse('comment-like-list', args=[self.comment.id])
    def test_list_all_comment_likes(self):
        all_commentlikes = []
        for c in range(3):
            all_commentlikes.append(CommentLikeFactory(comment=self.comment))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = CommentLikeSerializer(all_commentlikes, many=True, context={'request': response.wsgi_request})
        self.assertEqual(response.data['results'], serializer.data)
