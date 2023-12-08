from rest_framework import serializers
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validatorss
from accounts.models import User

class UserValidationMixin:
    def validate_password(self, value):
        user = User(
            username='username',
            email='email',
            password=value
            )
        try:
            validatorss.validate_password(password=value, user=user)
        except ValidationError as err:
            raise serializers.ValidationError(err.messages)
        return value

