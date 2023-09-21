# recipes/models.py - RecipeTag
RECIPE_TAG_NAME_LENGTH = 60
RECIPE_TAG_SLUG_LENGTH = 80
RECIPE_TAG_COLOR_LENGTH = 80

# recipes/models.py - Ingredient
INGREDIENT_NAME_LENGTH = 200
INGREDIENT_UNIT_LENGTH = 20

# recipes/models.py - Recipe
RECIPE_NAME_LENGTH = 255

# recipes/models.py, api/serializers.py
MIN_INGREDIENT_AMOUNT = 1
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 1440

# foodgram/settings.py, api/pagination.py,
DEFAULT_PAGE_SIZE = 6

# users/models.py - User
MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 150
