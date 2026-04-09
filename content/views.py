from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article, Newsletter
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .forms import ArticleForm, NewsletterForm
from collections import defaultdict
from .utils import notify_subscribers

# This file defines the view functions for the content app, handling article
# and newsletter operations such as listing, creating, editing, deleting, and
# approving content, as well as rendering the appropriate templates
# for each action.


# ---------------------------ARTICLES VIEWS----------------------------


@login_required
def article_list(request):
    '''
    Display articles based on user role.

    Journalist:
        Shows their articles grouped by publication.
        Independent articles grouped separately.

    Editor:
        Shows articles from assigned publications.
        Separates pending and approved articles.

    Defensive features:
    - Safe role checking
    - Query optimisation
    - Exception protection
    '''

    try:

        role = getattr(request.user, "role", None)

        # JOURNALIST VIEW
        if role == "journalist":

            articles = (
                Article.objects.filter(
                    journalist=request.user
                )
                .select_related(
                    "publication",
                    "publication__publisher"
                )
                .order_by("publication_date")
            )

            grouped_articles = defaultdict(list)

            for article in articles:

                if article.publication:

                    grouped_articles[
                        article.publication
                    ].append(article)

                else:

                    grouped_articles[
                        "Independent"
                    ].append(article)

            return render(
                request,
                "articles/article_list.html",
                {
                    "grouped_articles":
                    dict(grouped_articles),
                    "articles": articles
                }
            )

        # EDITOR VIEW
        if role == "editor":

            articles = (
                Article.objects.filter(
                    publication__editors=request.user
                )
                .select_related(
                    "publication",
                    "journalist"
                )
            )

            return render(
                request,
                "articles/article_list.html",
                {
                    "pending_articles":
                    articles.filter(
                        approval_status="pending"
                    ),

                    "approved_articles":
                    articles.filter(
                        approval_status="approved"
                    ),
                }
            )

        return redirect("home")

    except Exception:

        messages.error(
            request,
            "Unable to load article."
        )

        return redirect("home")


def all_articles(request):
    '''
    Display all approved articles.

    Defensive features:
    - Handles empty result sets
    - Prevents query failures
    - Provides user feedback
    '''

    try:

        articles = (
            Article.objects.filter(
                approval_status="approved"
            )
            .select_related(
                "publication",
                "journalist"
            )
            .order_by("publication_date")
        )

        if not articles.exists():

            messages.info(
                request,
                "No articles available yet."
            )

        return render(
            request,
            "articles/all_articles.html",
            {
                "articles": articles,
                "publication": None
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load articles."
        )

        return render(
            request,
            "articles/all_articles.html",
            {
                "articles": (),
                "publication": None
            }
        )


@login_required
def article_detail(request, pk):
    '''
    Display detailed view of a single article.

    Defensive features:
    - Safe object retrieval
    - Query optimisation
    - Exception protection
    '''

    try:

        article = get_object_or_404(
            Article.objects.select_related(
                "publication",
                "journalist"
            ),
            pk=pk
        )

        return render(
            request,
            "articles/article_detail.html",
            {
                "article": article
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load article."
        )

        return redirect("all_articles")


@login_required
def create_article(request):
    '''
    Create a new article.

    Defensive features:
    - Restricts access to journalists
    - Validates form input
    - Handles database errors safely
    - Provides user feedback
    '''

    if getattr(request.user, "role", None) != "journalist":

        raise PermissionDenied

    try:

        if request.method == "POST":

            form = ArticleForm(
                request.POST,
                user=request.user
            )

            if form.is_valid():

                article = form.save(commit=False)

                article.journalist = request.user

                # Independent journalists auto-approved
                if article.publication:

                    article.approval_status = "pending"

                else:

                    article.approval_status = "approved"

                article.save()

                messages.success(
                    request,
                    "Article published successfully."
                )

                return redirect("article_list")

            messages.error(
                request,
                "Please correct the errors."
            )

        else:

            form = ArticleForm(
                user=request.user
            )

        return render(
            request,
            "articles/article_create.html",
            {
                "form": form
            }
        )

    except Exception:

        messages.error(
            request,
            "Error saving article."
        )

        return redirect("article_list")


@login_required
def edit_article(request, pk):
    '''
    Edit an existing article.

    Defensive features:
    - Role-based access control
    - Ownership validation
    - Approval workflow protection
    - Exception handling
    '''

    try:

        article = get_object_or_404(
            Article.objects.select_related(
                "publication",
                "journalist"
            ),
            pk=pk
        )

        role = getattr(request.user, "role", None)

        # Journalist may only edit own articles
        if role == "journalist":

            if article.journalist != request.user:

                raise PermissionDenied

        # Editors may only edit their publications
        elif role == "editor":

            if (
                article.publication
                not in request.user.publications_joined.all()
            ):

                raise PermissionDenied

        else:

            raise PermissionDenied

        if request.method == "POST":

            form = ArticleForm(
                request.POST,
                instance=article,
                user=request.user
            )

            if form.is_valid():

                old_status = article.approval_status

                article = form.save(commit=False)

                # Re-submit rejected articles
                if old_status == "rejected":

                    article.approval_status = "pending"

                article.save()

                messages.success(
                    request,
                    "Article updated successfully."
                )

                return redirect("article_list")

            messages.error(
                request,
                "Please correct the errors."
            )

        else:

            form = ArticleForm(
                instance=article,
                user=request.user
            )

        return render(
            request,
            "articles/article_edit.html",
            {
                "form": form
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to update article."
        )

        return redirect("article_list")


@login_required
def delete_article(request, article_id):
    '''
    Delete an article.

    Defensive features:
    - Role-based access control
    - Ownership validation
    - Exception handling
    - User feedback
    '''

    try:

        article = get_object_or_404(
            Article.objects.select_related(
                "publication",
                "journalist"
            ),
            id=article_id
        )

        role = getattr(request.user, "role", None)

        if role not in ("journalist", "editor"):

            raise PermissionDenied

        # Journalist can only delete own articles
        if role == "journalist":

            if article.journalist != request.user:

                raise PermissionDenied

        # Editor can only delete publication articles
        if role == "editor":

            if (
                article.publication
                not in request.user.publications_joined.all()
            ):

                raise PermissionDenied

        article.delete()

        messages.success(
            request,
            "Article deleted successfully."
        )

    except PermissionDenied:

        messages.error(
            request,
            "You do not have permission."
        )

    except Exception:

        messages.error(
            request,
            "Unable to delete article."
        )

    return redirect("article_list")


@login_required
def approve_article(request, pk):
    '''
    Approve an article for publication.

    Defensive features:
    - Editor permission validation
    - Approval state protection
    - Safe object retrieval
    - Exception handling
    '''

    try:

        article = get_object_or_404(
            Article.objects.select_related(
                "publication"
            ),
            pk=pk
        )

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        if (
            article.publication and
            request.user in article.publication.editors.all()
        ):

            if article.approval_status == "approved":

                messages.info(
                    request,
                    "Article already approved."
                )

            else:

                article.approval_status = "approved"

                article.save()

                notify_subscribers(article)

                messages.success(
                    request,
                    "Article approved successfully."
                )

        else:

            messages.error(
                request,
                "Not authorised."
            )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Unable to approve article."
        )

    return redirect("article_list")


@login_required
def reject_article(request, pk):
    '''
    Reject an article.

    Defensive features:
    - Editor permission validation
    - Publication ownership checks
    - Exception handling
    - User feedback
    '''

    try:

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        article = get_object_or_404(
            Article.objects.select_related(
                "publication"
            ),
            pk=pk
        )

        if (
            not article.publication or
            request.user not in
            article.publication.editors.all()
        ):

            raise PermissionDenied

        article.approval_status = "rejected"

        article.save()

        messages.success(
            request,
            "Article rejected."
        )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Unable to reject article."
        )

    return redirect("article_list")


@login_required
def pending_articles(request):
    '''
    Display pending articles for editor approval.

    Defensive features:
    - Role-based access control
    - Publication ownership filtering
    - Query optimisation
    - Exception handling
    '''

    try:

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        articles = (
            Article.objects.filter(
                approval_status="pending",
                publication__editors=request.user
            )
            .select_related(
                "publication",
                "journalist"
            )
        )

        return render(
            request,
            "articles/pending_article.html",
            {
                "articles": articles
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
            "Unable to load pending articles."
        )

    return redirect("article_list")


# ---------------------------NEWSLETTERS VIEWS----------------------------


def newsletter_list(request):
    '''
    Display newsletters based on user role.

    Journalist:
        Shows their newsletters grouped by publication.
        Independent newsletters grouped separately.

    Editor:
        Shows newsletters from assigned publications.
        Separates pending and approved newsletters.

    Defensive features:
    - Safe role checking
    - Query optimisation
    - Exception protection
    '''

    try:

        role = getattr(request.user, "role", None)

        # JOURNALIST VIEW
        if role == "journalist":

            newsletters = (
                Newsletter.objects.filter(
                    journalist=request.user
                )
                .select_related(
                    "publication",
                    "publication__publisher"
                )
                .order_by("publication_date")
            )

            grouped_newsletters = defaultdict(list)

            for newsletter in newsletters:

                if newsletter.publication:

                    grouped_newsletters[
                        newsletter.publication
                    ].append(newsletter)

                else:

                    grouped_newsletters[
                        "Independent"
                    ].append(newsletter)

            return render(
                request,
                "newsletters/newsletters_list.html",
                {
                    "grouped_newsletters":
                    dict(grouped_newsletters),
                    "newsletters": newsletters
                }
            )

        # EDITOR VIEW
        if role == "editor":

            newsletters = (
                Newsletter.objects.filter(
                    publication__editors=request.user
                )
                .select_related(
                    "publication",
                    "journalist"
                )
            )

            return render(
                request,
                "newsletters/newsletters_list.html",
                {
                    "pending_newsletters":
                    newsletters.filter(
                        approval_status="pending"
                    ),

                    "approved_newsletters":
                    newsletters.filter(
                        approval_status="approved"
                    ),
                }
            )

        return redirect("home")

    except Exception:

        messages.error(
            request,
            "Unable to load newsletters."
        )

        return redirect("home")


def all_newsletters(request):
    '''
    Display all approved newsletters.

    Defensive features:
    - Handles empty result sets
    - Prevents query failures
    - Provides user feedback
    '''

    try:

        newsletters = (
            Newsletter.objects.filter(
                approval_status="approved"
            )
            .select_related(
                "publication",
                "journalist"
            )
            .order_by("publication_date")
        )

        if not newsletters.exists():

            messages.info(
                request,
                "No newsletters available yet."
            )

        return render(
            request,
            "newsletters/all_newsletters.html",
            {
                "newsletters": newsletters,
                "publication": None
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load newsletters."
        )

        return render(
            request,
            "newsletters/all_newsletters.html",
            {
                "newsletters": (),
                "publication": None
            }
        )


@login_required
def newsletter_detail(request, pk):
    '''
    Display detailed view of a single newsletter.

    Defensive features:
    - Safe object retrieval
    - Query optimisation
    - Exception protection
    '''

    try:

        newsletter = get_object_or_404(
            Newsletter.objects.select_related(
                "publication",
                "journalist"
            ),
            pk=pk
        )

        return render(
            request,
            "newsletters/newsletter_detail.html",
            {
                "newsletter": newsletter
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to load newsletter."
        )

        return redirect("all_newsletters")


@login_required
def create_newsletter(request):
    '''
    Create a new newsletter.

    Defensive features:
    - Restricts access to journalists
    - Validates form input
    - Handles database errors safely
    - Provides user feedback
    '''

    if getattr(request.user, "role", None) != "journalist":

        raise PermissionDenied

    try:

        if request.method == "POST":

            form = NewsletterForm(
                request.POST,
                user=request.user
            )

            if form.is_valid():

                newsletter = form.save(commit=False)

                newsletter.journalist = request.user

                # Independent journalists auto-approved
                if newsletter.publication:

                    newsletter.approval_status = "pending"

                else:

                    newsletter.approval_status = "approved"

                newsletter.save()

                messages.success(
                    request,
                    "Newsletter published successfully."
                )

                return redirect("newsletter_list")

            messages.error(
                request,
                "Please correct the errors."
            )

        else:

            form = NewsletterForm(
                user=request.user
            )

        return render(
            request,
            "newsletters/newsletter_create.html",
            {
                "form": form
            }
        )

    except Exception:

        messages.error(
            request,
            "Error saving newsletter."
        )

        return redirect("newsletter_list")


@login_required
def edit_newsletter(request, pk):
    '''
    Edit an existing newsletter.

    Defensive features:
    - Role-based access control
    - Ownership validation
    - Approval workflow protection
    - Exception handling
    '''

    try:

        newsletter = get_object_or_404(
            Newsletter.objects.select_related(
                "publication",
                "journalist"
            ),
            pk=pk
        )

        role = getattr(request.user, "role", None)

        # Journalist may only edit own newsletters
        if role == "journalist":

            if newsletter.journalist != request.user:

                raise PermissionDenied

        # Editors may only edit their publications
        elif role == "editor":

            if (
                newsletter.publication
                not in request.user.publications_joined.all()
            ):

                raise PermissionDenied

        else:

            raise PermissionDenied

        if request.method == "POST":

            form = NewsletterForm(
                request.POST,
                instance=newsletter,
                user=request.user
            )

            if form.is_valid():

                old_status = newsletter.approval_status

                newsletter = form.save(commit=False)

                # Re-submit rejected newsletters
                if old_status == "rejected":

                    newsletter.approval_status = "pending"

                newsletter.save()

                messages.success(
                    request,
                    "Newsletter updated successfully."
                )

                return redirect("newsletter_list")

            messages.error(
                request,
                "Please correct the errors."
            )

        else:

            form = NewsletterForm(
                instance=newsletter,
                user=request.user
            )

        return render(
            request,
            "newsletters/newsletter_edit.html",
            {
                "form": form
            }
        )

    except Exception:

        messages.error(
            request,
            "Unable to update newsletter."
        )

        return redirect("newsletter_list")


@login_required
def delete_newsletter(request, pk):
    '''
    Delete a newsletter.

    Defensive features:
    - Role-based access control
    - Ownership validation
    - Exception handling
    - User feedback
    '''

    try:

        newsletter = get_object_or_404(
            Newsletter.objects.select_related(
                "publication",
                "journalist"
            ),
            pk=pk
        )

        role = getattr(request.user, "role", None)

        if role not in ("journalist", "editor"):

            raise PermissionDenied

        # Journalist can only delete own newsletters
        if role == "journalist":

            if newsletter.journalist != request.user:

                raise PermissionDenied

        # Editor can only delete publication newsletters
        if role == "editor":

            if (
                newsletter.publication
                not in request.user.publications_joined.all()
            ):

                raise PermissionDenied

        newsletter.delete()

        messages.success(
            request,
            "Newsletter deleted successfully."
        )

    except PermissionDenied:

        messages.error(
            request,
            "You do not have permission."
        )

    except Exception:

        messages.error(
            request,
            "Unable to delete newsletter."
        )

    return redirect("newsletter_list")


@login_required
def approve_newsletter(request, pk):
    '''
    Approve a newsletter for publication.

    Defensive features:
    - Editor permission validation
    - Approval state protection
    - Safe object retrieval
    - Exception handling
    '''

    try:

        newsletter = get_object_or_404(
            Newsletter.objects.select_related(
                "publication"
            ),
            pk=pk
        )

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        if (
            newsletter.publication and
            request.user in newsletter.publication.editors.all()
        ):

            if newsletter.approval_status == "approved":

                messages.info(
                    request,
                    "Newsletter already approved."
                )

            else:

                newsletter.approval_status = "approved"

                newsletter.save()

                messages.success(
                    request,
                    "Newsletter approved successfully."
                )

        else:

            messages.error(
                request,
                "Not authorised."
            )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Unable to approve newsletter."
        )

    return redirect("newsletter_list")


@login_required
def reject_newsletter(request, pk):
    '''
    Reject a newsletter.

    Defensive features:
    - Editor permission validation
    - Publication ownership checks
    - Exception handling
    - User feedback
    '''

    try:

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        newsletter = get_object_or_404(
            Newsletter.objects.select_related(
                "publication"
            ),
            pk=pk
        )

        if (
            not newsletter.publication or
            request.user not in
            newsletter.publication.editors.all()
        ):

            raise PermissionDenied

        newsletter.approval_status = "rejected"

        newsletter.save()

        messages.success(
            request,
            "Newsletter rejected."
        )

    except PermissionDenied:

        messages.error(
            request,
            "Permission denied."
        )

    except Exception:

        messages.error(
            request,
            "Unable to reject newsletter."
        )

    return redirect("newsletter_list")


@login_required
def pending_newsletters(request):
    '''
    Display pending newsletters for editor approval.

    Defensive features:
    - Role-based access control
    - Publication ownership filtering
    - Query optimisation
    - Exception handling
    '''

    try:

        role = getattr(request.user, "role", None)

        if role != "editor":

            raise PermissionDenied

        newsletters = (
            Newsletter.objects.filter(
                approval_status="pending",
                publication__editors=request.user
            )
            .select_related(
                "publication",
                "journalist"
            )
        )

        return render(
            request,
            "newsletters/pending_newsletter.html",
            {
                "newsletters": newsletters
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
            "Unable to load pending newsletters."
        )

    return redirect("newsletter_list")
