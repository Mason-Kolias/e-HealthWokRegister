
from django import forms
from django.forms import BaseFormSet, formset_factory

from .models import (
    ApplicationDocument,
    LicenseRenewalApplication,
    MedicalLicense,
    MedicalLicenseApplication,
)


DOCUMENT_TYPES = [
    ("current_transcript", "Current Transcript"),
    ("current_school_id", "Current School ID"),
    ("school_confirmation", "School Confirmation Letter"),
    ("id_photo", "ID Sized Photo"),
    ("grade12_certificate", "National Grade 12 Certificate"),
    ("registration_fee_receipt", "Receipt for Registration Fee"),
]


class MedicalLicenseApplicationForm(forms.ModelForm):

    class Meta:

        model = MedicalLicenseApplication

        fields = [
            "full_name",
            "date_of_birth",
            "gender",
            "nationality",
            "phone_number",
            "email",
            "residential_address",
            "province",
            "district",
            "profession",
            "professional_registration_number",
            "specialization",
            "years_of_experience",
            "qualification",
            "institution",
            "campus",
            "institution_province",
            "country_of_qualification",
            "year_started",
            "year_completed",
            "graduation_status",
            "current_employer",
            "position",
            "workplace_province",
            "employment_start_date",
        ]

        widgets = {

            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full legal name",
                }
            ),

            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "gender": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "nationality": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter nationality",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter active phone number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter active email address",
                }
            ),

            "residential_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter current residential address",
                }
            ),

            "province": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "district": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter district",
                }
            ),

            "profession": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "professional_registration_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter registration number if applicable",
                }
            ),

            "specialization": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter specialization if applicable",
                }
            ),

            "years_of_experience": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Enter years of experience",
                }
            ),

            "qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter health profession qualification",
                }
            ),

            "institution": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "campus": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter campus",
                }
            ),

            "institution_province": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "country_of_qualification": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter country of qualification",
                }
            ),

            "year_started": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1900,
                    "max": 2100,
                    "placeholder": "Year started",
                }
            ),

            "year_completed": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1900,
                    "max": 2100,
                    "placeholder": "Year completed",
                }
            ),

            "graduation_status": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "current_employer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter current employer if applicable",
                }
            ),

            "position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter current position if applicable",
                }
            ),

            "workplace_province": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "employment_start_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        required_fields = [
         # Personal Information
    "full_name",
    "date_of_birth",
    "gender",
    "nationality",

    # Contact & Location
    "phone_number",
    "email",
    "residential_address",
    "province",
    "district",

    # Profession
    "profession",

    # Education & Graduation
    "qualification",
    "institution",
    "country_of_qualification",
    "year_completed",
    "graduation_status",
        ]
        for field_name in required_fields:

            if field_name in self.fields:

                self.fields[
                    field_name
                ].required = True

        optional_fields = [
       "professional_registration_number",
    "specialization",
    "years_of_experience",
    "campus",
    "institution_province",
    "year_started",
    "current_employer",
    "position",
    "workplace_province",
    "employment_start_date",
        ]
        

        for field_name in optional_fields:

            if field_name in self.fields:

                self.fields[
                    field_name
                ].required = False
                
        # =========================================================
# BETTER LABELS
# =========================================================

        self.fields["profession"].label = "Profession"
        self.fields["professional_registration_number"].label = (
    "Professional registration number (Optional)"
)
        self.fields["specialization"].label = (
    "Specialization (Optional)"
)
        self.fields["years_of_experience"].label = (
    "Years of experience (Optional)"
)
        






    

class ApplicationDocumentForm(forms.ModelForm):

    class Meta:

        model = ApplicationDocument

        fields = [
            "document_type",
            "document_file",
        ]

        widgets = {

            "document_type": forms.HiddenInput(),

            "document_file": forms.ClearableFileInput(
                attrs={
                    "class": "document-file-input",
                    "accept": ".pdf,.jpg,.jpeg,.png",
                }
            ),
        }

    def __init__(
        self,
        *args,
        application=None,
        document_type=None,
        **kwargs,
    ):

        self.application = application
        self.fixed_document_type = document_type

        if (
            application is not None
            and document_type
        ):

            existing_document = (
                ApplicationDocument.objects
                .filter(
                    application=application,
                    document_type=document_type,
                )
                .first()
            )

            if existing_document is not None:

                kwargs[
                    "instance"
                ] = existing_document

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            "document_type"
        ].required = False

        self.fields[
            "document_file"
        ].required = False

        if document_type:

            self.initial[
                "document_type"
            ] = document_type

            self.fixed_document_label = dict(
                DOCUMENT_TYPES
            ).get(
                document_type,
                "Required Document",
            )

        else:

            self.fixed_document_label = (
                "Required Document"
            )

    def clean_document_type(self):

        return self.fixed_document_type

    def clean_document_file(self):

        uploaded_file = (
            self.cleaned_data.get(
                "document_file"
            )
        )

        if not uploaded_file:

            if (
                self.instance
                and self.instance.pk
                and self.instance.document_file
            ):

                return self.instance.document_file

            raise forms.ValidationError(
                "Please upload this required document."
            )

        allowed_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
        }

        filename = uploaded_file.name.lower()

        if not any(
            filename.endswith(extension)
            for extension in allowed_extensions
        ):

            raise forms.ValidationError(
                "Only PDF, JPG, JPEG and PNG files are accepted."
            )

        if uploaded_file.size > 5 * 1024 * 1024:

            raise forms.ValidationError(
                "The document must not exceed 5 MB."
            )

        return uploaded_file

    def save(
        self,
        commit=True
    ):

        document = super().save(
            commit=False
        )

        document.application = (
            self.application
        )

        document.document_type = (
            self.fixed_document_type
        )

        if commit:

            document.save()

        return document


class FixedDocumentFormSet(BaseFormSet):

    def __init__(
        self,
        *args,
        application=None,
        **kwargs
    ):

        self.application = application

        super().__init__(
            *args,
            **kwargs
        )

    def get_form_kwargs(
        self,
        index
    ):

        kwargs = super().get_form_kwargs(
            index
        )

        document_type = None

        if (
            0 <= index
            < len(DOCUMENT_TYPES)
        ):

            document_type = (
                DOCUMENT_TYPES[index][0]
            )

        kwargs.update(
            {
                "application": self.application,
                "document_type": document_type,
            }
        )

        return kwargs

    def clean(self):

        super().clean()

        if any(self.errors):

            return

        if (
            len(self.forms)
            != len(DOCUMENT_TYPES)
        ):

            raise forms.ValidationError(
                "All required supporting documents must be provided."
            )

        uploaded_types = set()

        for form in self.forms:

            if not hasattr(
                form,
                "cleaned_data"
            ):

                continue

            if not form.cleaned_data:

                continue

            document_type = (
                form.cleaned_data.get(
                    "document_type"
                )
            )

            document_file = (
                form.cleaned_data.get(
                    "document_file"
                )
            )

            if (
                document_type
                and document_file
            ):

                uploaded_types.add(
                    document_type
                )

        required_types = {
            document_type
            for document_type, label
            in DOCUMENT_TYPES
        }

        missing_types = (
            required_types
            - uploaded_types
        )

        if missing_types:

            labels = dict(
                DOCUMENT_TYPES
            )

            missing_labels = [
                labels.get(
                    document_type,
                    document_type.replace(
                        "_",
                        " "
                    ).title(),
                )
                for document_type
                in sorted(
                    missing_types
                )
            ]

            raise forms.ValidationError(
                "The following required documents are missing: "
                + ", ".join(
                    missing_labels
                )
            )

    def save(
        self,
        commit=True
    ):

        saved_documents = []

        for form in self.forms:

            if not hasattr(
                form,
                "cleaned_data"
            ):

                continue

            if not form.cleaned_data:

                continue

            document_file = (
                form.cleaned_data.get(
                    "document_file"
                )
            )

            if not document_file:

                continue

            document = form.save(
                commit=False
            )

            document.application = (
                self.application
            )

            document.document_type = (
                form.fixed_document_type
            )

            if commit:

                document.save()

            saved_documents.append(
                document
            )

        return saved_documents


ApplicationDocumentFormSet = formset_factory(
    ApplicationDocumentForm,
    formset=FixedDocumentFormSet,
    extra=len(DOCUMENT_TYPES),
    max_num=len(DOCUMENT_TYPES),
    validate_max=True,
)


class LicenseRenewalApplicationForm(
    forms.ModelForm
):

    registration_number = forms.CharField(
        label="Registration Number",
        max_length=50,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your medical license number",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:

        model = LicenseRenewalApplication

        fields = [
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
                    "placeholder": "Enter your contact phone number",
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
        **kwargs
    ):

        super().__init__(
            *args,
            **kwargs
        )

        self.applicant = applicant

    def clean_registration_number(self):

        registration_number = (
            self.cleaned_data[
                "registration_number"
            ]
            .strip()
            .upper()
        )

        if not self.applicant:

            raise forms.ValidationError(
                "Your account could not be verified."
            )

        try:

            medical_license = (
                MedicalLicense.objects.get(
                    license_number=registration_number,
                    applicant=self.applicant,
                )
            )

        except MedicalLicense.DoesNotExist:

            raise forms.ValidationError(
                "The registration number does not belong "
                "to your account."
            )

        if medical_license.status not in {
            "active",
            "expired",
        }:

            raise forms.ValidationError(
                "This medical license cannot be renewed "
                "because it is not active or expired."
            )

        self.validated_medical_license = (
            medical_license
        )

        return registration_number

    def clean_payment_receipt(self):

        receipt = (
            self.cleaned_data.get(
                "payment_receipt"
            )
        )

        if not receipt:

            raise forms.ValidationError(
                "Please upload your renewal fee receipt."
            )

        allowed_types = [
            "application/pdf",
            "image/jpeg",
            "image/png",
        ]

        if (
            receipt.content_type
            not in allowed_types
        ):

            raise forms.ValidationError(
                "Only PDF, JPG, JPEG or PNG files are allowed."
            )

        if receipt.size > 5 * 1024 * 1024:

            raise forms.ValidationError(
                "The receipt must not exceed 5 MB."
            )

        return receipt

    def clean(self):

        cleaned_data = super().clean()

        registration_number = (
            cleaned_data.get(
                "registration_number"
            )
        )

        if (
            registration_number
            and self.applicant
        ):

            medical_license = (
                MedicalLicense.objects
                .filter(
                    license_number=registration_number,
                    applicant=self.applicant,
                    status__in=[
                        "active",
                        "expired",
                    ],
                )
                .first()
            )

            if medical_license:

                self.validated_medical_license = (
                    medical_license
                )

        return cleaned_data

    def save(
        self,
        commit=True
    ):

        renewal = super().save(
            commit=False
        )

        if hasattr(
            self,
            "validated_medical_license"
        ):

            renewal.medical_license = (
                self.validated_medical_license
            )

        if self.applicant:

            renewal.applicant = (
                self.applicant
            )

        if commit:

            renewal.save()

        return renewal

