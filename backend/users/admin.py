from django.contrib import admin

from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name',)
    search_fields = ('email', 'username', 'first_name', 'last_name',)
    list_filter = ('email', 'first_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'followed_author', 'subscription_date',)
    search_fields = ('follower__email', 'followed_author__email',)
