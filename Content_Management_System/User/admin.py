from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'city', 'state', 'address', 'is_staff')
