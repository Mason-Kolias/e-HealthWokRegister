
from django import forms

from .models import (
    LicenseRenewalApplication,
    MedicalLicense,
)


class LicenseRenewalApplicationForm(forms.ModelForm):

    registration_number = forms.CharField(
        label="Medical License / Registration Number",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your medical license number",
                "autocomplete": "off",
            }
        ),
        help_text=(
            "Enter the medical license number issued to you "
            "during your original registration."
        ),
    )

    class Meta:
        model = LicenseRenewalApplication

        fields = [
            "registration_number",
            "current_employer",
            "current_work_location",
            "contact_phone",
            "email",
            "payment_receipt",
        ]

        widgets = {
            "current_employer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your current employer",
                }
            ),

            "current_work_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your current work location",
                }
            ),

            "contact_phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your contact number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your email address",
                }
            ),

            "payment_receipt": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                }
            ),
        }

    def __init__(
        self,
        *args,
        applicant=None,
        **kwargs,
    ):
        self.applicant = applicant
        self.validated_medical_license = None

        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # If editing an existing renewal application,
        # display the current medical license number.
        # -------------------------------------------------

        if (
            self.instance
            and self.instance.pk
            and self.instance.medical_license_id
        ):
            self.fields[
                "registration_number"
            ].initial = (
                self.instance.medical_license.license_number
            )

    def clean_registration_number(self):

        registration_number = (
            self.cleaned_data
            .get("registration_number", "")
            .strip()
        )

        if not registration_number:
            raise forms.ValidationError(
                "Please enter your medical license number."
            )

        if not self.applicant:
            raise forms.ValidationError(
                "The health worker account could not be identified."
            )

        # -------------------------------------------------
        # IMPORTANT
        #
        # Both ACTIVE and EXPIRED medical licenses may
        # be used for annual license renewal.
        #
        # An expired license does NOT prevent renewal.
        # -------------------------------------------------

        try:
            medical_license = (
                MedicalLicense.objects
                .select_related(
                    "application",
                    "applicant",
                )
                .get(
                    license_number__iexact=registration_number,
                    applicant=self.applicant,
                    status__in=[
                        "active",
                        "expired",
                    ],
                )
            )

        except MedicalLicense.DoesNotExist:

            raise forms.ValidationError(
                "No active or expired medical license "
                "matching this registration number was "
                "found under your account."
            )

        # -------------------------------------------------
        # Prevent a revoked license from being renewed.
        # -------------------------------------------------

        if medical_license.status == "revoked":
            raise forms.ValidationError(
                "This medical license has been revoked "
                "and cannot be renewed."
            )

        self.validated_medical_license = medical_license

        return registration_number

    def clean(self):

        cleaned_data = super().clean()

        if not self.applicant:
            return cleaned_data

        registration_number = cleaned_data.get(
            "registration_number"
        )

        if not registration_number:
            return cleaned_data

        # -------------------------------------------------
        # Confirm again that the license belongs to the
        # logged-in health worker.
        #
        # Expired licenses are deliberately allowed.
        # -------------------------------------------------

        medical_license = (
            MedicalLicense.objects
            .select_related(
                "application",
                "applicant",
            )
            .filter(
                applicant=self.applicant,
                license_number__iexact=registration_number,
                status__in=[
                    "active",
                    "expired",
                ],
            )
            .first()
        )

        if not medical_license:

            self.add_error(
                "registration_number",
                (
                    "This registration number does not "
                    "belong to an active or expired medical "
                    "license under your account."
                ),
            )

            return cleaned_data

        self.validated_medical_license = medical_license

        return cleaned_data

    def save(
        self,
        commit=True,
    ):

        renewal = super().save(
            commit=False
        )

        if self.applicant:
            renewal.applicant = self.applicant

        if self.validated_medical_license:
            renewal.medical_license = (
                self.validated_medical_license
            )

        if commit:
            renewal.save()

        return renewal

