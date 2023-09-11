from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from users.permissions import (IsAuthorOrAdminOrReadOnly,
                               IsUserOrAdminOrReadOnly)

from . import constants
from .filters import IngredientsFilter, RecipesFilter
from .pagination import CustomApiPagination
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    '''Вьюсет для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsUserOrAdminOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет для рецептов.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    pagination_class = CustomApiPagination
    filterset_class = RecipesFilter

    def get_queryset(self):
        '''Получение queryset.'''
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        '''Выбор сериализатора исходя из запроса.'''
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        else:
            return RecipeCreateUpdateSerializer

    def perform_create(self, serializer):
        '''Метод берёт и сохраняет автора из запроса.'''
        if self.request.method == 'POST':
            serializer.save(author=self.request.user)

    @action(
        methods=[
            'post', 'delete'], detail=True, permission_classes=[
                permissions.IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        '''Добавление, удаление, проверка для избранного.'''
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        if request.method == 'POST':
            if Favorite.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Этот рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        recipe_to_del = Favorite.objects.filter(user=request.user,
                                                recipe=recipe)
        if recipe_to_del:
            recipe_to_del.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'errors': 'Такого рецепта в избранном нет.'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post', 'delete'],
            detail=True, permission_classes=[permissions.IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        '''Добавление и удаление рецепта из списка покупок.'''
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(
                    user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            recipe_to_del = ShoppingCart.objects.filter(
                user=request.user, recipe=recipe)
            if recipe_to_del:
                recipe_to_del.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'Такого рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'], detail=False,
        permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        '''Логика скачивания списка покупок для пользователя.'''
        recipe_list = request.user.shopping_cart.all().values_list(
            'recipe', flat=True)
        recipes = Recipe.objects.filter(id__in=recipe_list)
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes).select_related('ingredient')
        ingredients_dict = {}
        for recipe_ingredient in recipe_ingredients:
            measurement_unit = recipe_ingredient.ingredient.measurement_unit
            ingredient_name = recipe_ingredient.ingredient.name
            amount = recipe_ingredient.amount
            ingredient_id = recipe_ingredient.ingredient.id
            if ingredient_id in ingredients_dict:
                ingredients_dict[ingredient_name] += amount
                ingredients_dict[ingredient_name] = (
                    f'{ingredients_dict[ingredient_name]}{measurement_unit}')
            else:
                ingredients_dict[ingredient_name] = amount
                ingredients_dict[ingredient_name] = (
                    f'{ingredients_dict[ingredient_name]} {measurement_unit}')
        ingredients_list = []

        for name, amount in ingredients_dict.items():
            ingredients_list.append(f'{name}: ({amount})')

        pdfmetrics.registerFont(
            TTFont(
                'DejaVuSans',
                'C:/Dev/foodgram-project-react/static/DejaVuSans.ttf',
                'utf-8'))

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"')

        pdf = canvas.Canvas(response)
        pdf.setFont('DejaVuSans', size=14)
        text1 = f'{request.user}, Ваш список покупок сегодня:'
        pdf.drawString(constants.LEFT_INDENT, constants.HEIGHT_OFFSET, text1)
        for string in ingredients_list:
            constants.HEIGHT_OFFSET -= 50
            pdf.drawString(
                constants.LEFT_INDENT, constants.HEIGHT_OFFSET, string)

        pdf.showPage()
        pdf.save()

        return response


class IngredientViewSet(viewsets.ModelViewSet):
    '''Вьюсет для ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsUserOrAdminOrReadOnly, )
    filter_backends = (IngredientsFilter, )
    search_fields = ('^name',)
