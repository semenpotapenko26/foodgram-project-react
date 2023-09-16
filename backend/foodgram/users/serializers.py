from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import CustomUser, Follow


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор для пользователей.'''
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user,
                                         author=obj).exists()
        return False


class UserPostSerializer(serializers.ModelSerializer):
    '''Сериализатор для добавления пользователей.'''
    class Meta:
        model = CustomUser
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'password')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Не называйтесь "me"')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DemoRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для ограниеченности полей рецепта.'''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    '''Сериализатор для подписок.'''
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def get_recipes(self, obj):
        '''Получение рецептов'''
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.id)
        if limit:
            recipes = recipes[:int(limit)]
        return DemoRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        '''Получение кол-во рецептов'''
        return Recipe.objects.filter(author=obj).count()
