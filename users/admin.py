from django.contrib import admin
from .models import CustomUser

# This file registers the CustomUser model with the Django admin. This allows
# administrators to manage users through the Django admin interface.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    '''
    Admin configuration for CustomUser model.
    '''

    list_display = (

        'username',

        'role',

        'editor_status',

        'is_staff',

    )

    list_filter = (

        'role',

        'editor_status',
    )
