from rest_framework import permissions
from accounts.models import User
from rest_framework.exceptions import PermissionDenied


class IsObjectAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True
        else:
            raise PermissionDenied(detail='You are not authorized to perform this action.')


class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            if obj == request.user:
                return True
            else:
                raise PermissionDenied(detail='You are not authorized to perform this action.')
        elif obj.user == request.user:
            return True
        else:
            raise PermissionDenied(detail='You are not authorized to perform this action.')

        
        