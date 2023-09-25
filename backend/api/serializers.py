from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, validators
from rest_framework.generics import get_object_or_404

from djoser.serializers import UserSerializer as DjoserUserSerializer

from api.utils import Base64ImageField
from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    FavoriteRecipe,
    Recipe,
    ShoppingCart,
    RecipeTag,
)
from users.models import Subscription
from core import constants

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(label='New Password')
    current_password = serializers.CharField(label='Current Password')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(username=user.email, password=current_password):
            raise serializers.ValidationError(
                'Unable to log in with provided credentials.')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=('ingredient', 'recipe'),
            )
        ]


class FavoriteOrSubscribeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count',)
        read_only_fields = ('is_subscribed', 'recipes_count',)

    def validate(self, data):
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError(
                {'errors': 'Cannot subscribe to yourself.'}
            )
        if Subscription.objects.filter(user=user_id,
                                       author=author_id).exists():
            raise serializers.ValidationError(
                {'errors': 'Cannot subscribe again.'}
            )
        data['user'] = get_object_or_404(User, id=user_id)
        data['author'] = get_object_or_404(User, id=author_id)
        return data

    def get_is_subscribed(self, obj):
        return Subscription.objects.filter(user=obj.user,
                                           author=obj.author).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = FavoriteOrSubscribeSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    ingredients = IngredientInRecipeSerializer(many=True,
                                               read_only=True,
                                               source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(method_name="user_shopping_cart")

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart',)

    @classmethod
    def create_ingredients(cls, recipe, ingredients):
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe,
                                ingredient_id=ingredient.get('id'),
                                amount=ingredient.get('amount'))
             for ingredient in ingredients])

    def create(self, validated_data):
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(
            recipe=instance, ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(recipe=obj, user=user).exists()

    def user_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()

    def validate(self, data):
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Add at least one ingredient for the recipe.')
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) < constants.MIN_INGREDIENT_AMOUNT:
                errors.append(
                    f'Ingredient with id - {ingredient["id"]} '
                    f'must be integer and ≥{constants.MIN_INGREDIENT_AMOUNT}.'
                )
            if ingredient['id'] in added_ingredients:
                errors.append('Cannot add the same ingredient')
            added_ingredients.append(ingredient['id'])
        tags = data.get('tags')
        if len(tags) > len(set(tags)):
            errors.append('Cannot use the same tag more than once.')
        cooking_time = float(data.get('cooking_time'))
        if cooking_time < constants.MIN_COOKING_TIME:
            errors.append(
                f'Cooking time must be '
                f'≥{constants.MIN_COOKING_TIME} minute.'
            )
        if cooking_time > constants.MAX_COOKING_TIME:
            errors.append(
                f'Cooking time must be '
                f'≤ {constants.MAX_COOKING_TIME} minutes.'
            )
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data
