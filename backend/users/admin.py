from django.contrib import admin

from users.models import Subscription, User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name',)
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', 'created')
    search_fields = ('user__email', 'author__email')
