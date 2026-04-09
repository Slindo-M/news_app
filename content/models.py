from django.db import models

# Create your models here.
# This file defines the data models for the content app, including Article
# and Newsletter.


class Article(models.Model):
    '''
    Represents an article written by a journalist.

    Defensive features:
    - Automatically approves independent articles
    - Prevents invalid approval states
    - Maintains publication integrity
    '''

    title = models.CharField(max_length=255)

    content = models.TextField()

    publication_date = models.DateTimeField(auto_now_add=True)

    update_date = models.DateTimeField(auto_now=True)

    journalist = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'journalist'},
        related_name='articles'
    )

    publication = models.ForeignKey(
        'publication.Publication',
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True
    )

    approval_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ),
        default='pending'
    )

    def save(self, *args, **kwargs):

        try:

            # Independent journalists auto-approved
            if self.publication is None:
                self.approval_status = 'approved'

        except Exception:
            pass

        super().save(*args, **kwargs)

    def __str__(self):

        return self.title


class Newsletter(models.Model):
    '''
    Represents a newsletter written by a journalist.

    Defensive features:
    - Automatically approves independent newsletters
    - Protects approval workflow
    '''

    title = models.CharField(max_length=255)

    content = models.TextField()

    publication_date = models.DateTimeField(auto_now_add=True)

    update_date = models.DateTimeField(auto_now=True)

    journalist = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'journalist'},
        related_name='newsletters'
    )

    publication = models.ForeignKey(
        'publication.Publication',
        on_delete=models.CASCADE,
        related_name='newsletters',
        null=True,
        blank=True
    )

    approval_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ),
        default='pending'
    )

    def save(self, *args, **kwargs):

        try:

            # Independent journalists auto-approved
            if self.publication is None:
                self.approval_status = 'approved'

        except Exception:
            pass

        super().save(*args, **kwargs)

    def __str__(self):

        return self.title
