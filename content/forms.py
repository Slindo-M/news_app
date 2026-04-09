'''
Forms for creating and editing articles and newsletters in the news
application.
'''
from django import forms
from .models import Article, Newsletter
from publication.models import Publication

# This file defines forms for creating and editing articles and newsletters.
# It includes custom logic to filter publication choices based on the
# journalist's approved publications and
# to hide the publication field for independent journalists.


class ArticleForm(forms.ModelForm):
    '''
    Form for creating and editing articles.

    Defensive features:
    - Restricts publication choices to approved publications
    - Validates title and publication input
    - Prevents unauthorized publication selection
    - Handles possible runtime errors safely
    '''

    class Meta:
        model = Article

        fields = ['title', 'content', 'publication']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'publication': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        try:

            if self.user:

                # Only publications where journalist is approved
                self.fields['publication'].queryset = (
                    Publication.objects.filter(
                        approved_journalists=self.user
                    )
                )

                # Hide field if independent journalist
                if getattr(self.user, 'role', None) == 'independent':

                    self.fields['publication'].widget = forms.HiddenInput()

        except Exception:
            # Defensive fallback to prevent form crash
            pass

    def clean_title(self):

        title = self.cleaned_data.get('title')

        if not title:
            raise forms.ValidationError(
                'Title cannot be empty.'
            )

        if len(title) < 5:
            raise forms.ValidationError(
                'Title must be at least 5 characters long.'
            )

        return title

    def clean_publication(self):

        publication = self.cleaned_data.get('publication')

        if self.user and getattr(self.user, 'role', None) != 'independent':

            if not publication:

                raise forms.ValidationError(
                    'Publication is required.'
                )

            if not Publication.objects.filter(
                id=publication.id,
                approved_journalists=self.user
            ).exists():

                raise forms.ValidationError(
                    'You are not approved for this publication.'
                )

        return publication


class NewsletterForm(forms.ModelForm):
    '''
    Form for creating newsletters.

    Defensive features:
    - Restricts publication access
    - Validates user input
    - Prevents unauthorized submissions
    - Handles unexpected errors safely
    '''

    class Meta:
        model = Newsletter

        fields = ['title', 'content', 'publication']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'publication': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        try:

            if self.user:

                # Only publications where journalist is approved
                self.fields['publication'].queryset = (
                    Publication.objects.filter(
                        approved_journalists=self.user
                    )
                )

                # Hide field if independent journalist
                if getattr(self.user, 'role', None) == 'independent':

                    self.fields['publication'].widget = forms.HiddenInput()

        except Exception:
            # Prevent unexpected crashes
            pass

    def clean_title(self):

        title = self.cleaned_data.get('title')

        if not title:

            raise forms.ValidationError(
                'Title cannot be empty.'
            )

        if len(title) < 5:

            raise forms.ValidationError(
                'Title must be at least 5 characters long.'
            )

        return title

    def clean_publication(self):

        publication = self.cleaned_data.get('publication')

        if self.user and getattr(self.user, 'role', None) != 'independent':

            if not publication:

                raise forms.ValidationError(
                    'Publication is required.'
                )

            if not Publication.objects.filter(
                id=publication.id,
                approved_journalists=self.user
            ).exists():

                raise forms.ValidationError(
                    'Invalid publication selection.'
                )

        return publication
