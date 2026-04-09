from rest_framework import serializers
from .models import Article

# This file defines serializers for the content app, which convert Article
# model instances to JSON format for API responses.


class ArticleSerializer(serializers.ModelSerializer):
    '''
    Serializer for approved articles.

    Defensive features:
    - Prevents modification of journalist field
    - Handles null publications safely
    '''

    journalist = serializers.CharField(
        source='journalist.username',
        read_only=True
    )

    publication = serializers.CharField(
        source='publication.name',
        allow_null=True,
        read_only=True
    )

    class Meta:

        model = Article

        fields = (
            'id',
            'title',
            'content',
            'journalist',
            'publication',
            'publication_date'
        )

        read_only_fields = (
            'id',
            'journalist',
            'publication_date'
        )
