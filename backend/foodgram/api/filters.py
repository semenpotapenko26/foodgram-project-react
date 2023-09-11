from django_filters import rest_framework as filters
from recipes.models import CustomUser, Recipe, Tag
from rest_framework.filters import SearchFilter


class IngredientsFilter(SearchFilter):
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    '''Фильтры для рецептов.'''
    author = filters.ModelChoiceFilter(
        queryset=CustomUser.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = [
            'tags', 'author', 'is_favorited', 'is_in_shopping_cart'
        ]

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientFilter(SearchFilter):
    '''Фильтры для ингредиентов.'''
    search_param = 'name'
