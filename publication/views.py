from django.shortcuts import render, get_object_or_404, redirect
from .models import Publication, Publisher
from users.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages

# This file contains the view functions for the publication app, which handle
# displaying the list of publications, publication details, and managing
# subscriptions and applications for journalists and editors.


def publication_list(request):
    '''
    Display all publications.

    Defensive features:
    - Safe query execution
    - Exception handling
    '''

    try:

        publications = Publication.objects.all()

        return render(
            request,
            "publications/publication_list.html",
            {
                "publications": publications
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load publications."
        )

        return render(
            request,
            "publications/publication_list.html",
            {
                "publications": ()
            }
        )


def publisher_detail(request, pk):
    '''
    Display publisher and its publications.

    Defensive features:
    - Safe query execution
    - Exception handling
    - Handles missing relationships safely
    '''

    try:

        publisher = get_object_or_404(
            Publisher,
            pk=pk
        )

        publications = Publication.objects.filter(
            publisher=publisher
        )

        return render(
            request,
            "publications/publisher_detail.html",
            {
                "publisher": publisher,
                "publications": publications
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load publisher."
        )

        return redirect("publication_list")


def publication_detail(request, pk):
    '''
    Display publication details and related content.

    Defensive features:
    - Safe query execution
    - Exception handling
    - Handles missing relationships safely
    '''

    try:

        publication = get_object_or_404(
            Publication.objects.select_related(
                "publisher"
            ).prefetch_related(
                "editors",
                "approved_journalists"
            ),
            pk=pk
        )

        articles = publication.articles.all()

        newsletters = publication.newsletters.all()

        return render(
            request,
            "publications/publication_detail.html",
            {
                "publication": publication,
                "publisher": publication.publisher,
                "editors": publication.editors.all(),
                "journalists":
                publication.approved_journalists.all(),
                "articles": articles,
                "newsletters": newsletters
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load publication."
        )

        return redirect("publication_list")


@login_required
def unsubscribe_publication(request, pk):
    '''
    Allow readers to unsubscribe from publisher.

    Defensive features:
    - Permission validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    if getattr(request.user, "role", None) != "reader":

        raise PermissionDenied

    try:

        publisher = get_object_or_404(
            Publisher,
            pk=pk
        )

        if request.user not in publisher.subscribers.all():

            messages.info(
                request,
                "You are not subscribed."
            )

        else:

            publisher.subscribers.remove(
                request.user
            )

            messages.success(
                request,
                "Unsubscribed successfully."
            )

    except Exception:

        messages.error(
            request,
            "Could not unsubscribe."
        )

    return redirect(
        "publication_detail",
        pk=pk
    )


@login_required
def subscribe_publication(request, publisher_id):
    '''
    Allow readers to subscribe to publisher.

    Defensive features:
    - Permission validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    if getattr(request.user, "role", None) != "reader":

        raise PermissionDenied

    try:

        publisher = get_object_or_404(
            Publisher,
            id=publisher_id
        )

        if request.user in publisher.subscribers.all():

            messages.info(
                request,
                "Already subscribed."
            )

        else:

            publisher.subscribers.add(
                request.user
            )

            messages.success(
                request,
                "Subscribed successfully."
            )

    except Exception:

        messages.error(
            request,
            "Subscription failed."
        )

    return redirect("publication_list")


@login_required
def journalist_join(request, pk):
    '''
    Allow journalist to apply to publication.

    Defensive features:
    - Permission validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    if getattr(request.user, "role", None) != "journalist":

        raise PermissionDenied

    try:

        publication = get_object_or_404(
            Publication,
            pk=pk
        )

        if request.user in publication.approved_journalists.all():

            messages.info(
                request,
                "Already a member."
            )

        elif request.user in publication.pending_journalists.all():

            messages.info(
                request,
                "Application already pending."
            )

        else:

            publication.pending_journalists.add(
                request.user
            )

            messages.success(
                request,
                "Application submitted."
            )

    except Exception:

        messages.error(
            request,
            "Application failed."
        )

    return redirect(
        "publication_detail",
        pk=pk
    )


@login_required
def editor_signup(request, pk):
    '''
    Allow editors to apply to publication.

    Defensive features:
    - Permission validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    try:

        publication = get_object_or_404(
            Publication,
            pk=pk
        )

        if getattr(request.user, "role", None) != "editor":

            raise PermissionDenied

        if request.user in publication.editors.all():

            messages.info(
                request,
                "Already an editor."
            )

        elif request.user in publication.pending_editors.all():

            messages.info(
                request,
                "Application pending."
            )

        else:

            publication.pending_editors.add(
                request.user
            )

            messages.success(
                request,
                "Editor application submitted."
            )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Application failed."
        )

    return redirect(
        "publication_detail",
        pk=pk
    )


@login_required
def pending_journalists(request):
    '''
    Display pending journalist applications.

    Defensive features:
    - Editor approval validation
    - Safe query filtering
    - Exception protection
     - Handles missing relationships safely
    '''

    try:

        if getattr(request.user, "role", None) != "editor":

            raise PermissionDenied

        publications = Publication.objects.filter(
            editors=request.user
        ).prefetch_related(
            "pending_journalists"
        )

        return render(
            request,
            "dashboards/pending_journalist.html",
            {
                "publications": publications
            }
        )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Unable to load applications."
        )

    return redirect("editor_dashboard")


@login_required
def approve_journalist(
    request,
    publication_id,
    user_id
):
    '''
    Approve journalist application.

    Defensive features:
    - Editor approval validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    try:

        publication = get_object_or_404(
            Publication,
            id=publication_id
        )

        if request.user not in publication.editors.all():

            raise PermissionDenied

        journalist = get_object_or_404(
            CustomUser,
            id=user_id
        )

        if journalist in publication.pending_journalists.all():

            publication.pending_journalists.remove(
                journalist
            )

            publication.approved_journalists.add(
                journalist
            )

            messages.success(
                request,
                "Journalist approved."
            )

        else:

            messages.info(
                request,
                "No pending application."
            )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Approval failed."
        )

    return redirect("pending_journalists")


@login_required
def reject_journalist(
    request,
    publication_id,
    user_id
):
    '''
    Reject journalist application.

    Defensive features:
    - Editor approval validation
    - Safe query execution
    - Exception handling
     - Handles missing relationships safely
    '''

    try:

        publication = get_object_or_404(
            Publication,
            id=publication_id
        )

        if request.user not in publication.editors.all():

            raise PermissionDenied

        journalist = get_object_or_404(
            CustomUser,
            id=user_id
        )

        if journalist in publication.pending_journalists.all():

            publication.pending_journalists.remove(
                journalist
            )

            messages.success(
                request,
                "Application rejected."
            )

        else:

            messages.info(
                request,
                "No pending application."
            )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Rejection failed."
        )

    return redirect("pending_journalists")
