from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from publication.models import Publication
from django import forms

# This file contains the forms for the users app, which handle user
# registration and profile management.


class CustomUserCreationForm(UserCreationForm):
    '''
    Custom user registration form.

    Defensive features:
    - Role validation
    - Publication assignment validation
    - Password styling
    '''

    publications = forms.ModelMultipleChoiceField(
        queryset=Publication.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check"}
        )
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
    )

    class Meta:

        model = CustomUser

        fields = (
            'username',
            'email',
            'role',
            'publications',
            'password1',
            'password2'
        )

        widgets = {
            "username": forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            "email": forms.EmailInput(
                attrs={'class': 'form-control'}
            ),

            "role": forms.Select(
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields[
            "publications"
        ].queryset = Publication.objects.order_by(
            "name"
        )

    def clean(self):

        cleaned_data = super().clean()

        role = cleaned_data.get("role")

        publications = cleaned_data.get(
            "publications"
        )

        if role == "editor" and not publications:

            raise forms.ValidationError(
                "Editors must select at least one "
                "publication."
            )

        return cleaned_data
