import factory
from accounts.models import Profile, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'user {n}')
    email = factory.Sequence(lambda n: f'email{n}@gmail.com')
    password = 'Testado123@'


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        
    user = factory.SubFactory(UserFactory)
