from django.db import models

# This file defines the models for the publication app, which include
# Publisher and Publication.


class Publisher(models.Model):
    '''
    Represents a publishing organisation.

    Defensive features:
    - Subscriber management
    - Safe relationships
    '''

    name = models.CharField(max_length=255)

    description = models.TextField(blank=True)

    subscribers = models.ManyToManyField(
        'users.CustomUser',
        blank=True,
        related_name='subscribed_publishers'
    )

    class Meta:

        ordering = ("name",)

    def __str__(self):

        return self.name


class Publication(models.Model):
    '''
    Represents a publication under a publisher.

    Defensive features:
    - Editor approval workflow
    - Journalist approval workflow
    - Controlled role relationships
    '''

    name = models.CharField(max_length=255)

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='publications'
    )

    description = models.TextField(blank=True)

    editors = models.ManyToManyField(
        'users.CustomUser',
        blank=True,
        related_name='editor_publications',
        limit_choices_to={
            'role': 'editor',
            'editor_status': 'approved'
        }
    )

    pending_editors = models.ManyToManyField(
        'users.CustomUser',
        blank=True,
        related_name='editor_applications',
        limit_choices_to={
            'role': 'editor'
        }
    )

    approved_journalists = models.ManyToManyField(
        'users.CustomUser',
        blank=True,
        related_name='publications_joined',
        limit_choices_to={
            'role': 'journalist'
        }
    )

    pending_journalists = models.ManyToManyField(
        'users.CustomUser',
        blank=True,
        related_name='journalist_applications'
    )

    class Meta:

        ordering = ("name",)

    def __str__(self):

        return f"{self.name} ({self.publisher.name})"
