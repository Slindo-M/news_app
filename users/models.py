from django.db import models
from django.contrib.auth.models import AbstractUser

# This file defines the CustomUser model, which extends Django's built-in
# AbstractUser to support different user roles (reader, journalist, editor)
# and their specific fields and relationships.


class CustomUser(AbstractUser):
    '''
    Custom user model supporting readers, journalists,
    and editors.

    Defensive features:
    - Role-based behaviour
    - Editor approval workflow
    - Subscription relationships
    '''

    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('journalist', 'Journalist'),
        ('editor', 'Editor'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader'
    )

    editor_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Reader-specific fields

    subscribed_journalists = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='followers'
    )

    class Meta:

        ordering = ("username",)

    def __str__(self):

        return self.username

    # Journalist-specific fields

    @property
    def articles_published(self):

        if self.role == 'journalist':

            return self.articles.filter(
                publication=None
            )

        return self.articles.none()

    @property
    def newsletters_published(self):

        if self.role == 'journalist':

            return self.newsletters.filter(
                publication=None
            )

        return self.newsletters.none()
