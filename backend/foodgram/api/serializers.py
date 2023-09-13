from django.db import transaction
from django.db.models import F
from django.forms import ValidationError
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор для тегов.'''
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов.'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор для безопасных запросов рецепта.'''
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author',
                  'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name', 'image',
                  'text', 'cooking_time')

    def get_ingredients(self, obj):
        '''Получение поля ингредиентов.'''
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F(
                'recipe_ingredients__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        '''Получение поля избранного.'''
        user = self.context.get('request').user
        return (
            user.is_authenticated and Favorite.objects.filter(
                user=user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        '''Получение поля списка покупок.'''
        user = self.context.get('request').user
        return (
            user.is_authenticated and ShoppingCart.objects.filter(
                user=user, recipe=obj).exists())


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''Serializer для небезопасных запросов рецепта.'''
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        '''Получение поля ингредиентов.'''
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F(
                'recipe_ingredients__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        '''Получение поля избранного.'''
        user = self.context.get('request').user
        return Favorite.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        '''Получение поля списка покупок.'''
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def validate(self, data):
        '''Валидация данных для рецепта.'''
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags_ids or not ingredients:
            raise ValidationError('Мало данных.')
        return data

    @transaction.atomic
    def create(self, validated_data):
        '''Создание рецепта.'''
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient['amount'])
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        '''Обновление рецепта.'''
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            ingredient_obj = Ingredient.objects.get(id=ingredient['id'])
            RecipeIngredient.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient_obj,
                amount=ingredient['amount'])
        instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор для избранного.'''
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'coocking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для списка покупок.'''
    id = serializers.PrimaryKeyRelatedField(source='recipe', read_only=True)
    name = serializers.ReadOnlyField(source='recipe.name', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)
    coocking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'coocking_time')
