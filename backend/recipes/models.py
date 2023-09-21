from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from colorfield.fields import ColorField

from core import constants

User = get_user_model()


class RecipeTag(models.Model):
    name = models.CharField(
        'Tag Name',
        max_length=constants.RECIPE_TAG_NAME_LENGTH,
        unique=True,
    )
    color = ColorField(
        'Color in HEX',
        max_length=constants.RECIPE_TAG_COLOR_LENGTH,
        unique=True,
        validators=[
            validators.RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message="Color must be in HEX format (e.g., #RRGGBB).",
            ),
        ],
    )
    slug = models.SlugField(
        'Unique Slug',
        max_length=constants.RECIPE_TAG_SLUG_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Recipe Tag'
        verbose_name_plural = 'Recipe Tags'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Ingredient Name',
        max_length=constants.INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        'Measurement Unit',
        max_length=constants.INGREDIENT_UNIT_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe Author',
    )
    name = models.CharField(
        'Recipe Name',
        max_length=constants.RECIPE_NAME_LENGTH,
    )
    image = models.ImageField(
        'Image URL',
        upload_to='recipe/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        'Recipe Description'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        RecipeTag,
        verbose_name='Recipe Tags',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking Time in Minutes',
        validators=[
            validators.MinValueValidator(
                constants.MIN_COOKING_TIME,
                message='Minimum cooking time: 1 minute!',
            ),
            validators.MaxValueValidator(
                constants.MAX_COOKING_TIME,
                message='Maximum cooking time: 1440 minutes!',
            )
        ],
    )
    pub_date = models.DateTimeField(
        'Publication Date',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='ingredient_quantities',
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='recipe_quantities',
    )
    amount = models.PositiveIntegerField(
        default=constants.MIN_INGREDIENT_AMOUNT,
        validators=(
            validators.MinValueValidator(
                constants.MIN_INGREDIENT_AMOUNT,
                message='Minimum ingredient amount is 1!'),
        ),
        verbose_name='Amount',
    )

    class Meta:
        verbose_name = 'Ingredient Quantity'
        verbose_name_plural = 'Ingredient Quantities'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient'),
        )


class RecipeUserList(models.Model):
    """Shared base class for Favorites and Shopping Cart."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
    )

    class Meta:
        abstract = True
        ordering = ('user', 'recipe')


class FavoriteRecipe(RecipeUserList):
    class Meta(RecipeUserList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_list_user',
            ),
        )

    def __str__(self):
        return (f'User @{self.user.username} '
                f'added {self.recipe} to favorites.')


class ShoppingCart(RecipeUserList):
    class Meta(RecipeUserList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart_list_user'
            ),
        )

    def __str__(self):
        return (f'User {self.user} '
                f'added {self.recipe.name} to the shopping cart.')
