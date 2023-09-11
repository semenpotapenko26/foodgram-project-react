from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    '''
    Неавторизованным пользователям разрешён только просмотр.
    Если пользователь админ или владелец записи, то остальной доступ разрешен.
    '''
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
        )


class IsUserOrAdminOrReadOnly(permissions.BasePermission):
    '''
    Неавторизованным пользователям разрешён только просмотр.
    Если пользователь админ
    или обычный пользователь, то остальной доступ разрешён.
    '''
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )
