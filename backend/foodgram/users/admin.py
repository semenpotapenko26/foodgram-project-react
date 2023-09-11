from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Follow


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'first_name', 'last_name', 'password']


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ['user', 'author']
