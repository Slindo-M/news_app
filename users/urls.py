from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


# This file defines the URL patterns for the users app, mapping URLs to
# corresponding view functions for handling user registration, login, and
# subscription management for readers.


urlpatterns = [

    # Registration
    path("register/", views.register, name="register"),

    # Login
    path("login/",
         auth_views.LoginView.as_view(template_name="registration/login.html"),
         name="login"),

    # Subscriptions
    path(
        "subscribe/journalist/<int:journalist_id>/",
        views.subscribe_journalist,
        name="subscribe_journalist"
    ),

    path(
        "unsubscribe/journalist/<int:journalist_id>/",
        views.unsubscribe_journalist,
        name="unsubscribe_journalist"
    ),

]
