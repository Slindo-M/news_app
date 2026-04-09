from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import CustomUser
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.core.exceptions import PermissionDenied

# This file contains the view functions for the users app, which handle user
# registration and subscription management for readers.


def register(request):
    '''
    Register new users and handle role workflows.

    Defensive features:
    - Role validation
    - Application workflow protection
    - Duplicate prevention
    - Exception handling
    '''

    try:

        if request.method == "POST":

            form = CustomUserCreationForm(
                request.POST
            )

            if form.is_valid():

                user = form.save(
                    commit=False
                )

                publications = (
                    form.cleaned_data.get(
                        "publications"
                    )
                )

                # Set editor approval state
                if user.role == "editor":

                    user.editor_status = "pending"

                else:

                    user.editor_status = "approved"

                user.save()

                # Journalist workflow
                if user.role == "journalist":

                    if publications:

                        for publication in publications:

                            if (
                                user not in
                                publication.pending_journalists.all()
                            ):

                                publication.pending_journalists.add(
                                    user
                                )

                        messages.info(
                            request,
                            "Application submitted "
                            "for approval."
                        )

                    else:

                        messages.success(
                            request,
                            "Registered as independent "
                            "journalist."
                        )

                # Editor workflow
                elif user.role == "editor":

                    if publications:

                        for publication in publications:

                            if (
                                user not in
                                publication.pending_editors.all()
                            ):

                                publication.pending_editors.add(
                                    user
                                )

                    messages.info(
                        request,
                        "Editor application submitted."
                    )

                else:

                    messages.success(
                        request,
                        "Account created successfully."
                    )

                login(request, user)

                return redirect("home")

            messages.error(
                request,
                "Please correct the errors."
            )

        else:

            form = CustomUserCreationForm()

    except Exception:

        messages.error(
            request,
            "Registration failed."
        )

        return redirect("register")

    return render(
        request,
        "registration/register.html",
        {
            "form": form
        }
    )


@login_required
def unsubscribe_journalist(request, journalist_id):
    '''
    Allow readers to unsubscribe from journalists.

    Defensive features:
    - Role validation
    - Safe query filtering
    '''

    if getattr(request.user, "role", None) != "reader":

        raise PermissionDenied

    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role="journalist"
    )

    try:

        if journalist not in (
            request.user.subscribed_journalists.all()
        ):

            messages.info(
                request,
                "Not subscribed."
            )

        else:

            request.user.subscribed_journalists.remove(
                journalist
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

    return redirect("article_list")


@login_required
def subscribe_journalist(request, journalist_id):
    '''
    Allow readers to subscribe to journalists.

    Defensive features:
    - Role validation
    - Duplicate prevention
    - Exception handling
    '''

    if getattr(request.user, "role", None) != "reader":

        raise PermissionDenied

    journalist = get_object_or_404(
        CustomUser,
        id=journalist_id,
        role="journalist"
    )

    try:

        if journalist in (
            request.user.subscribed_journalists.all()
        ):

            messages.info(
                request,
                "Already subscribed."
            )

        else:

            request.user.subscribed_journalists.add(
                journalist
            )

            messages.success(
                request,
                "Subscribed to journalist."
            )

    except Exception:

        messages.error(
            request,
            "Subscription failed."
        )

    return redirect("article_list")
