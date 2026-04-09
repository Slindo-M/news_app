from django.core.mail import send_mail
from django.conf import settings

# This file contains utility functions for the content app, such as sending
# emails to subscribers when a new article is published.


def notify_subscribers(article):
    '''
    Notify subscribers when a new article is published.

    Defensive features:
    - Handles missing relationships safely
    - Prevents duplicate notifications
    - Ignores users without email addresses
    - Prevents email sending crashes
    '''

    try:

        # Journalist followers
        journalist_subscribers = (
            article.journalist.followers.all()
        )

        # Publisher subscribers (if publication exists)
        if article.publication:

            publisher_subscribers = (
                article.publication.publisher
                .subscribers.all()
            )

        else:

            publisher_subscribers = []

        # Combine subscribers without duplicates
        all_subscribers = set(
            list(journalist_subscribers) +
            list(publisher_subscribers)
        )

        # Collect valid email addresses
        emails = [
            user.email
            for user in all_subscribers
            if getattr(user, "email", None)
        ]

        # Send notifications if emails exist
        if emails:

            send_mail(
                subject=(
                    f"New article published: "
                    f"{article.title}"
                ),
                message=(
                    f"{article.title} has just "
                    f"been published."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=emails,
                fail_silently=True
            )

    except Exception:
        # Prevent notification failures from
        # breaking article publishing
        pass
