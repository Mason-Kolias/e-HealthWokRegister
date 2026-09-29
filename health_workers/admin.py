from django.contrib import admin
from .models import MedicalLicenseApplication, ApplicationDocument


@admin.register(MedicalLicenseApplication)
class MedicalLicenseApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "application_number",
        "full_name",
        "profession",
        "status",
        "submitted_at",
    )

    list_filter = (
        "status",
        "profession",
        "province",
    )

    search_fields = (
        "application_number",
        "full_name",
        "professional_registration_number",
        "national_id",
    )


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "application",
        "document_type",
        "uploaded_at",
    )

    list_filter = (
        "document_type",
    )