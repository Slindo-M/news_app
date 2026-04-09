from django.shortcuts import render, redirect
from publication.models import Publication
from users.models import CustomUser
from content.models import Article, Newsletter
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# This file contains the view functions for the core app, which handle the
# landing page, home page, and dashboards for different user roles (reader,
# journalist, editor). Each view function retrieves the necessary data and
# renders the appropriate template based on the user's role and authentication
# status.


def home(request):
    '''
    Display homepage with featured publications.

    Defensive features:
    - Safe query execution
    - Exception protection
    '''

    try:

        publications = Publication.objects.all()[:6]

        return render(
            request,
            "home.html",
            {
                "publications": publications
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load homepage."
        )

        return render(
            request,
            "home.html",
            {
                "publications": ()
            }
        )


def landing_page(request):
    '''
    Redirect authenticated users to their dashboard.
    '''

    if not request.user.is_authenticated:

        return redirect("home")

    return redirect("home_redirect")


@login_required
def reader_dashboard(request):
    '''
    Display reader subscriptions.

    Defensive features:
    - Safe relationship queries
    - Exception protection
    '''

    try:

        subscribed_publishers = (
            request.user.subscribed_publishers.all()
        )

        subscribed_journalists = (
            request.user.subscribed_journalists.all()
        )

        if (
            not subscribed_publishers.exists() and
            not subscribed_journalists.exists()
        ):

            messages.info(
                request,
                "You have no subscriptions yet."
            )

        return render(
            request,
            "dashboards/reader_home.html",
            {
                "publishers": subscribed_publishers,
                "journalists": subscribed_journalists
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load dashboard."
        )

        return redirect("home")


@login_required
def journalist_dashboard(request):
    '''
    Display journalist articles and newsletters.

    Defensive features:
    - Query optimisation
    - Exception handling
    '''

    try:

        articles = Article.objects.filter(
            journalist=request.user
        ).order_by("publication_date")

        newsletters = Newsletter.objects.filter(
            journalist=request.user
        ).order_by("publication_date")

        return render(
            request,
            "dashboards/journalist_home.html",
            {
                "articles": articles,
                "newsletters": newsletters
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load dashboard."
        )

        return redirect("home")


@login_required
def editor_dashboard(request):
    '''
    Display editor moderation dashboard.

    Defensive features:
    - Editor approval validation
    - Safe query filtering
    - Exception protection
    '''

    try:

        if getattr(
            request.user,
            "editor_status",
            None
        ) != "approved":

            return render(
                request,
                "dashboards/editor_pending.html"
            )

        pending_articles = Article.objects.filter(
            publication__editors=request.user,
            approval_status="pending"
        )

        pending_journalists = CustomUser.objects.filter(
            journalist_applications__editors=request.user
        )

        pending_newsletters = Newsletter.objects.filter(
            publication__editors=request.user,
            approval_status="pending"
        )

        return render(
            request,
            "dashboards/editor_home.html",
            {
                "pending_articles_count":
                pending_articles.count(),

                "pending_journalists_count":
                pending_journalists.count(),

                "pending_newsletters_count":
                pending_newsletters.count()
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load dashboard."
        )

        return redirect("home")


@login_required
def home_redirect(request):
    '''
    Redirect users to role-based dashboards.

    Defensive features:
    - Safe role detection
    - Fallback redirect
    '''

    role = getattr(request.user, "role", None)

    if role == "reader":

        return redirect("reader_dashboard")

    if role == "journalist":

        return redirect("journalist_dashboard")

    if role == "editor":

        return redirect("editor_dashboard")

    messages.error(
        request,
        "Account role not recognised."
    )

    return redirect("home")
