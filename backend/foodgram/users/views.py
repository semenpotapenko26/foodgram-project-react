from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomApiPagination

from .models import CustomUser, Follow
from .serializers import FollowSerializer, UserPostSerializer, UserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    '''Кастомный вьюсет для пользователей.'''
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    add_serializer = FollowSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = CustomApiPagination

    def get_serializer_class(self):
        '''Метод для выбора сериализатора.'''
        if self.action == 'create':
            return UserPostSerializer
        return UserSerializer

    @action(methods=['post'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        '''Метод для смены пароля.'''
        context = {'request': request}
        serializer = SetPasswordSerializer(data=request.data, context=context)
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.data['new_password']
            self.request.user.set_password(new_password)
            self.request.user.save()
            return Response('Пароль успешно изменен.',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer._errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request, *args, **kwargs):
        '''Метод для страницы об авторе.'''
        context = {'request': request}
        serializer = UserSerializer(request.user, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        '''Меотод для подписки на других авторов.'''
        author = get_object_or_404(CustomUser, id=kwargs.get('pk'))
        if request.method == 'POST':
            if author == request.user:
                return Response(
                    {'errors': 'Как вы подпишетесь на самого себя?'},
                    status=status.HTTP_400_BAD_REQUEST)
            follow, is_created = Follow.objects.get_or_create(
                user=request.user, author=author)
            if not is_created:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST)
            context = {
                'request': request}
            serializer = FollowSerializer(author, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_from_subscriptions(self, request, *args, **kwargs):
        '''Меотод для отписки на других авторов.'''
        author = get_object_or_404(CustomUser, id=kwargs.get('pk'))
        subscription = Follow.objects.filter(author=author)
        if subscription:
            subscription.delete()
            return Response({'errors': 'Вы отписались от этого шарлотана.'},
                            status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'errors': 'Вы и так на него не подписаны'})

    @action(methods=['get'], detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        '''Метод для отображения подписок.'''
        subscriptions = CustomUser.objects.filter(following__user=request.user)
        context = {'request': request}
        paginate = self.paginate_queryset(subscriptions)
        serializer = FollowSerializer(paginate, context=context, many=True)
        return self.get_paginated_response(serializer.data)
