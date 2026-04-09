from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer

# API view to get articles from subscribed journalists and publishers


@api_view(['GET'])
def subscribed_articles(request):
    '''
    Retrieve approved articles from journalists and publishers
    the authenticated user is subscribed to.

    Returns:
        Response: JSON list of articles or error message.

    Raises:
        401: If user not authenticated
        500: If server error occurs
    '''

    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required.'},
            status=401
        )

    try:
        user = request.user

        journalists = user.subscribed_journalists.all()
        publishers = user.subscribed_publishers.all()

        if not journalists and not publishers:
            return Response(
                {'message': 'No subscriptions found'},
                status=200
            )

        articles = Article.objects.filter(
            approval_status='approved',
            journalist__in=journalists
        ) | Article.objects.filter(
            approval_status='approved',
            publication__publisher__in=publishers
        )

        articles = articles.distinct()

        serializer = ArticleSerializer(articles, many=True)

        return Response(serializer.data)

    except Exception:

        return Response(
            {'error': 'An unexpected error occurred'},
            status=500
        )
