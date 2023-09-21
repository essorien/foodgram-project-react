from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes.models import (
    Ingredient,
    Recipe,
    IngredientInRecipe,
    FavoriteRecipe,
    ShoppingCart,
    RecipeTag,
)
from core import constants


class RecipeIngredientsAdmin(admin.StackedInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredient',)
    min_num = constants.MIN_INGREDIENT_AMOUNT


@admin.register(Recipe)
class RecipeListAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientsAdmin,)
    list_display = ('author', 'name', 'text',
                    'get_favorite_count', 'display_image')
    search_fields = (
        'name', 'cooking_time',
        'author__username', 'ingredients__name')
    list_filter = ('pub_date', 'tags')

    @admin.display(description='Электронная почта автора')
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join(str(tag) for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @admin.display(description='Избранное')
    def get_favorite_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Картинка')
    def display_image(self, obj):
        if obj.image:
            image_url = obj.image.url
            return mark_safe(f'<img src="{image_url}" width="100" height="100" />')
        return "No Image"


@admin.register(RecipeTag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')
