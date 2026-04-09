from django.urls import path
from . import views
from . import api_views

# This file defines the URL patterns for the content app, mapping URLs to
# corresponding view functions for handling article and newsletter operations,
# as well as API endpoints for subscribed articles.

urlpatterns = [

    # Articles URLS
    path(
        "articles/",
        views.all_articles,
        name="all_articles"
    ),

    path(
        "my-articles/",
        views.article_list,
        name="article_list"),

    path(
        'publication/<int:publication_id>articles/',
        views.article_list,
        name='publication_articles'
    ),

    path(
        "<int:pk>/",
        views.article_detail,
        name="article_detail"
    ),

    path(
        "create/",
        views.create_article,
        name="create_article"
    ),

    path(
        "<int:pk>/edit/",
        views.edit_article,
        name="edit_article"
    ),

    path(
        "<int:article_id>/delete/",
        views.delete_article,
        name="delete_article"
    ),

    path(
        "article/<int:pk>/approve/",
        views.approve_article,
        name="approve_article"
    ),

    path(
        "pending-articles/",
        views.pending_articles,
        name="pending_articles"
    ),

    path(
        "<int:pk>/reject/",
        views.reject_article,
        name="reject_article"
    ),

    # Newsletters URLS
    path(
        'newsletter/<int:pk>/',
        views.newsletter_detail,
        name="newsletter_detail"
    ),

    path(
        "newsletters/",
        views.all_newsletters,
        name="all_newsletters"
    ),

    path(
        "my-newsletters/",
        views.newsletter_list,
        name="newsletter_list"
    ),

    path(
        "newsletters/create/",
        views.create_newsletter,
        name="create_newsletter"
    ),

    path(
        "newsletters/<int:pk>/edit/",
        views.edit_newsletter,
        name="edit_newsletter"
    ),

    path(
        "newsletters/<int:pk>/delete/",
        views.delete_newsletter,
        name="delete_newsletter"
    ),

    path(
        "newsletter/<int:pk>/approve/",
        views.approve_newsletter,
        name="approve_newsletter"
    ),

    path(
        "pending-newsletters/",
        views.pending_newsletters,
        name="pending_newsletters"
    ),

    path(
        "newsletter/<int:pk>/reject/",
        views.reject_newsletter,
        name="reject_newsletter"
    ),

    # API URLS
    path(
        "api/subscribed-articles/",
        api_views.subscribed_articles,
        name="subscribed_articles"
    ),

]
