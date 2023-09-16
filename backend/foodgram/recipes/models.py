from django.db import models
from users.models import CustomUser

from .constants import CHOICE_COLOR


class Ingredient(models.Model):
    '''Модель для ингредиентов.'''
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Tag(models.Model):
    '''Модель для тегов.'''
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True, choices=CHOICE_COLOR)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    '''Модель для рецептов.'''
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(upload_to='images/')
    cooking_time = models.PositiveIntegerField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredient')

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    '''Модель для связи рецептов и ингредиентов.'''
    recipe = models.ForeignKey(
        Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients')
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    '''Модель для избранного.'''
    user = models.ForeignKey(
        CustomUser, related_name='favorite', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, related_name='favorite', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.recipe)


class ShoppingCart(models.Model):
    '''Модель для списка покупок.'''
    user = models.ForeignKey(
        CustomUser, related_name='shopping_cart', on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, related_name='shopping_cart', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.recipe)
