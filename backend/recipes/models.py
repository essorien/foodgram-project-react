from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class RecipeTag(models.Model):
    name = models.CharField(
        'Tag Name',
        max_length=60,
        unique=True,
    )
    color = models.CharField(
        'Color in HEX',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Unique Slug',
        max_length=80,
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
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Measurement Unit',
        max_length=20,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

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
        max_length=255,
    )
    image = models.ImageField(
        'Image URL',
        # upload_to='recipe/',
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
                1,
                message='Minimum cooking time: 1 minute!',
            ),
            validators.MaxValueValidator(
                1440,
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
        default=1,
        validators=(
            validators.MinValueValidator(
                1, message='Minimum ingredient amount is 1!'),
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
    """
    Favorite Recipe Model.
    """

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
    """
    Shopping Cart Model.
    """

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
