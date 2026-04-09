from django.contrib import admin
from .models import Article, Newsletter

# This file registers the Article and Newsletter models with the Django
# admin. This allows administrators to manage articles and newsletters
# through the Django admin interface.

admin.site.register(Article)
admin.site.register(Newsletter)
