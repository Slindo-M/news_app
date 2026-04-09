'''
Test cases for the content app in the news application.
'''
from django.test import TestCase
from django.urls import reverse
from users.models import CustomUser
from .models import Article

# This file contains test cases for the content app, specifically testing the
# API endpoint that returns articles from journalists a reader is subscribed
# to.


class ArticleAPITest(TestCase):
    '''
    Test suite for subscribed articles API.

    Verifies that readers only see articles from journalists
    they are subscribed to and that authentication is required.
    '''

    def setUp(self):
        '''
        Create test users and sample article data.
        '''

        # Create reader user
        self.reader = CustomUser.objects.create_user(
            username="reader",
            password="test123",
            role="reader"
        )

        # Create journalist
        self.journalist = CustomUser.objects.create_user(
            username="journalist",
            password="test123",
            role="journalist"
        )

        # Subscribe reader to journalist
        self.reader.subscribed_journalists.add(
            self.journalist
        )

        # Create approved article
        self.article = Article.objects.create(
            title="API Test",
            content="Testing",
            journalist=self.journalist,
            approval_status="approved"
        )

    def test_reader_gets_subscribed_articles(self):
        '''
        Test that reader receives articles from subscribed
        journalists.
        '''

        # Login reader
        self.client.login(
            username="reader",
            password="test123"
        )

        response = self.client.get(
            reverse('subscribed_articles')
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data), 1)

    def test_reader_does_not_get_unsubscribed_articles(self):
        '''
        Test that reader does not receive articles from
        journalists they are not subscribed to.
        '''

        other_journalist = CustomUser.objects.create_user(
            username="other",
            password="test123",
            role="journalist"
        )

        Article.objects.create(
            title="Wrong article",
            content="Should not appear",
            journalist=other_journalist,
            approval_status="approved"
        )

        self.client.login(
            username="reader",
            password="test123"
        )

        response = self.client.get(
            reverse('subscribed_articles')
        )

        self.assertEqual(len(response.data), 1)

    def test_authentication_required(self):
        '''
        Test that unauthenticated users cannot access
        subscribed articles endpoint.
        '''

        response = self.client.get(
            reverse('subscribed_articles')
        )

        self.assertEqual(response.status_code, 401)
