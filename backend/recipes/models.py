from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    Tag model.
    """
    name = models.CharField(
        'Tag name',
        max_length=80,
        unique=True,
    )

    color = models.CharField(
        'HEX Color',
        max_length=7,
        default='#00FFFF',
        unique=True,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Invalid format!',
            )
        ],
    )

    slug = models.SlugField(
        'Slug',
        max_length=80,
        unique=True,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    Ingredient model.
    """
    name = models.CharField(
        'Ingredient Name',
        max_length=255,
    )
    measurement_unit = models.CharField(
        'Ingredient Measurement Unit',
        max_length=25,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name}, ({self.measurement_unit}).'


class Recipe(models.Model):
    """
    Recipe model.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe Author',
    )
    name = models.CharField(
        'Recipe Name',
        max_length=220,
    )
    image = models.ImageField(
        'Image URL on the Website',
        upload_to='static/recipe/',
        blank=True,
        null=True,
    )
    text = models.TextField(
        'Recipe Description'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking Time in Minutes',
        validators=[
            MinValueValidator(1, 'Minimum cooking time 1 minute!'),
            MaxValueValidator(1440, 'Maximum cooking time 24 hours!')
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
        return self.name


class IngredientForRecipe(models.Model):
    """
    Model for the amount of ingredients in a recipe.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
        related_name='ingredients',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Ingredient Amount',
        validators=[
            MinValueValidator(1, 'Minimum ingredient amount: 1!'),
        ]
    )

    class Meta:
        verbose_name = 'Ingredient Amount'
        verbose_name_plural = 'Ingredient Amounts'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient'),
        ]

    def __str__(self):
        return f'Contains in {self.recipe.name}'


class RecipeUserList(models.Model):
    """
    Class for Favorites and Shopping Cart.
    """
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
    Favorite Recipe model.
    """

    class Meta(RecipeUserList.Meta):
        default_related_name = 'favorite_list'
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_list_user',
            ),
        ]

    def __str__(self):
        return (f'User @{self.user.username} '
                f'added {self.recipe} to favorites.')


class ShoppingCart(RecipeUserList):
    """
    Shopping Cart model.
    """

    class Meta(RecipeUserList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_cart_list_user'
            ),
        ]

    def __str__(self):
        return (f'User {self.user} '
                f'added {self.recipe.name} to the shopping cart.')
