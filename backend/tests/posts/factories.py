import factory
from posts.models import Post, Tag, PostLike, Comment, CommentLike
from tests.accounts.factories import UserFactory

class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        
    name = factory.Sequence(lambda n: f'tag{n}')
    

class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
    
    title = factory.Faker('sentence', nb_words=4)
    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)


class PostLikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PostLike
    
    user = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    content = factory.Faker('text')
    author = factory.SubFactory(UserFactory)        
    post = factory.SubFactory(PostFactory)
    
    
class CommentLikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentLike
    
    user = factory.SubFactory(UserFactory)
    comment = factory.SubFactory(CommentFactory)
