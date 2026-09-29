from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your first name",
            }
        ),
    )

    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your last name",
            }
        ),
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your username",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email address",
            }
        ),
    )

    profile_photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png",
            }
        ),
    )

    remove_profile_photo = forms.BooleanField(
        required=False,
        label="Remove profile photo",
    )

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)

        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields["first_name"].initial = (
                self.user_instance.first_name
            )

            self.fields["last_name"].initial = (
                self.user_instance.last_name
            )

            self.fields["username"].initial = (
                self.user_instance.username
            )

            self.fields["email"].initial = (
                self.user_instance.email
            )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        users = User.objects.filter(
            email__iexact=email
        )

        if self.user_instance:
            users = users.exclude(
                pk=self.user_instance.pk
            )

        if users.exists():
            raise forms.ValidationError(
                "This email address is already associated with another account."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        users = User.objects.filter(
            username__iexact=username
        )

        if self.user_instance:
            users = users.exclude(
                pk=self.user_instance.pk
            )

        if users.exists():
            raise forms.ValidationError(
                "This username is already associated with another account."
            )

        return username

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")

        if not photo:
            return None

        allowed_types = {
            "image/jpeg",
            "image/png",
        }

        content_type = getattr(
            photo,
            "content_type",
            None,
        )

        if content_type and content_type not in allowed_types:
            raise forms.ValidationError(
                "Please upload a JPG or PNG image."
            )

        if photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Profile photo must be smaller than 5 MB."
            )

        return photo