from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.viewsets import ReadOnlyModelViewSet

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet

from .filters import IngredientFilter, RecipeFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    FavoriteOrSubscribeSerializer,
    RecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
    UserSerializer,
    UserPasswordSerializer,
)
from .utils import collect_shopping_cart
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeTag,
    ShoppingCart,
)
from users.models import Subscription

User = get_user_model()


class SetPasswordView(APIView):
    def post(self, request):
        serializer = UserPasswordSerializer(data=request.data,
                                            context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed!'},
                            status=status.HTTP_201_CREATED)
        return Response({'error': 'Enter valid data!'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValueError('Cannot subscribe to yourself.')
            serializer = SubscribeSerializer(
                Subscription.objects.create(user=request.user, author=author),
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Subscription.objects.filter(user=request.user,
                                           author=author).exists():
                Subscription.objects.filter(user=request.user,
                                            author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Cannot unsubscribe(no subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        serializer = SubscribeSerializer(
            self.paginate_queryset(
                Subscription.objects.filter(user=request.user)
            ),
            many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = RecipeTag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def new_favorite_or_cart(self, model, user, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteOrSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_favorite_or_cart(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Recipe already removed!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.new_favorite_or_cart(FavoriteRecipe, request.user, pk)
        return self.remove_favorite_or_cart(FavoriteRecipe, request.user, pk)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.new_favorite_or_cart(ShoppingCart, request.user, pk)
        return self.remove_favorite_or_cart(ShoppingCart, request.user, pk)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_cart(request)
