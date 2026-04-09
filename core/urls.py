from django.urls import path
from . import views

# This file defines the URL patterns for the core app, mapping URLs to
# corresponding view functions for handling the landing page, home page, and
# dashboards for different user roles.

urlpatterns = [

    # Landing and Home Page URLs
    path('', views.landing_page, name='landing_page'),
    path('home/', views.home, name='home'),
    path('home-redirect/', views.home_redirect, name='home_redirect'),

    # Dashboards URLs
    path("reader/", views.reader_dashboard, name="reader_dashboard"),
    path("journalist/",
         views.journalist_dashboard,
         name="journalist_dashboard"),
    path("editor/", views.editor_dashboard, name="editor_dashboard"),
]
