from django.contrib import admin
from .models import Publisher, Publication

# This file registers the Publisher and Publication models with the Django
# admin. This allows administrators to manage publishers and publications
# through the Django admin interface.

admin.site.register(Publisher)
admin.site.register(Publication)
