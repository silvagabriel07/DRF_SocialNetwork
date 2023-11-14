import factory
from accounts.models import Profile, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: f'user{n+1}')
    email = factory.Sequence(lambda n: f'email{n+1}@gmail.com')
    password = factory.PostGenerationMethodCall('set_password', 'password')


