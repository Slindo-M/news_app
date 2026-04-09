from django.urls import path
from . import views

urlpatterns = [

    path('', views.publication_list, name='publication_list'),
    path('publisher/<int:pk>/',
         views.publisher_detail,
         name='publisher_detail'),
    path(
        "subscribe/publication/<int:publisher_id>/",
        views.subscribe_publication,
        name="subscribe_publication"
    ),

    path(
        "unsubscribe/publication/<int:pk>/",
        views.unsubscribe_publication,
        name="unsubscribe_publication"
    ),

    path(
        'publication/<int:pk>/',
        views.publication_detail,
        name="publication_detail"
    ),

    path(
        'publication/<int:pk>/journalist',
        views.journalist_join,
        name='journalist_join'
    ),

    path(
        'publication/<int:pk>/editor/',
        views.editor_signup,
        name="editor_signup"
    ),

    path(
        'pending/journalists/',
        views.pending_journalists,
        name="pending_journalists"
        ),

    path(
        'approve/<int:publication_id>/<int:user_id>/',
        views.approve_journalist,
        name="approve_journalist"
        ),

    path(
        'reject/<int:publication_id>/<int:user_id>/',
        views.reject_journalist,
        name="reject_journalist"
        ),
]
