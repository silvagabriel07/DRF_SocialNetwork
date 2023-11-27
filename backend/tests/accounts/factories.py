import factory
from accounts.models import User, Follow, Profile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        
    username = factory.Sequence(lambda n: f'user{n+1}')
    email = factory.Sequence(lambda n: f'email{n+1}@gmail.com')
    password = factory.django.Password('ConfPassw123@')


class FollowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follow
        
    followed = factory.SubFactory(UserFactory)
    follower = factory.SubFactory(UserFactory)
    
