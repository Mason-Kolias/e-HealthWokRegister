from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from health_workers.models import (
    ApplicationDocument,
    LicenseRenewalApplication,
    MedicalLicense,
    MedicalLicenseApplication,
)


@login_required
def health_worker_records(request):

    if request.user.role != "registrar":
        return redirect("home")

    records = (
        MedicalLicenseApplication.objects
        .filter(
            status__in=[
                "approved",
                "license_generated",
            ]
        )
        .select_related(
            "applicant",
            "license",
        )
        .order_by(
            "full_name",
            "created_at",
        )
    )

    search_query = request.GET.get(
        "search",
        "",
    ).strip()

    selected_profession = request.GET.get(
        "profession",
        "",
    ).strip()

    selected_province = request.GET.get(
        "province",
        "",
    ).strip()

    selected_license_status = request.GET.get(
        "license_status",
        "",
    ).strip()

    if search_query:

        records = records.filter(
            Q(full_name__icontains=search_query)
            |
            Q(applicant__first_name__icontains=search_query)
            |
            Q(applicant__last_name__icontains=search_query)
            |
            Q(applicant__username__icontains=search_query)
            |
            Q(applicant__email__icontains=search_query)
            |
            Q(application_number__icontains=search_query)
            |
            Q(license__license_number__icontains=search_query)
            |
            Q(professional_registration_number__icontains=search_query)
        )

    if selected_profession:

        records = records.filter(
            profession=selected_profession
        )

    if selected_province:

        records = records.filter(
            province=selected_province
        )

    if selected_license_status:

        if selected_license_status == "no_license":

            records = records.filter(
                license__isnull=True
            )

        else:

            records = records.filter(
                license__status=selected_license_status
            )

    total_records = (
        MedicalLicenseApplication.objects
        .filter(
            status__in=[
                "approved",
                "license_generated",
            ]
        )
        .count()
    )

    active_licenses = (
        MedicalLicense.objects
        .filter(
            status="active",
            application__status__in=[
                "approved",
                "license_generated",
            ],
        )
        .count()
    )

    expired_licenses = (
        MedicalLicense.objects
        .filter(
            status="expired",
            application__status__in=[
                "approved",
                "license_generated",
            ],
        )
        .count()
    )

    revoked_licenses = (
        MedicalLicense.objects
        .filter(
            status="revoked",
            application__status__in=[
                "approved",
                "license_generated",
            ],
        )
        .count()
    )

    profession_choices = (
        MedicalLicenseApplication.PROFESSION_CHOICES
    )

    province_choices = (
        MedicalLicenseApplication.PROVINCE_CHOICES
    )

    context = {
        "records": records,

        "total_records": total_records,

        "active_licenses": active_licenses,

        "expired_licenses": expired_licenses,

        "revoked_licenses": revoked_licenses,

        "profession_choices": profession_choices,

        "province_choices": province_choices,

        "search_query": search_query,

        "selected_profession": selected_profession,

        "selected_province": selected_province,

        "selected_license_status": selected_license_status,
    }

    return render(
        request,
        "registrar/health_worker_records.html",
        context,
    )


@login_required
def health_worker_record_detail(
    request,
    application_id,
):

    if request.user.role != "registrar":
        return redirect("home")

    application = get_object_or_404(
        MedicalLicenseApplication.objects
        .select_related(
            "applicant",
            "license",
            "reviewed_by",
        ),
        id=application_id,
        status__in=[
            "approved",
            "license_generated",
        ],
    )

    documents = (
        ApplicationDocument.objects
        .filter(
            application=application,
        )
        .order_by(
            "document_type",
        )
    )

    license_record = getattr(
        application,
        "license",
        None,
    )

    renewal_history = (
        LicenseRenewalApplication.objects
        .filter(
            medical_license=license_record,
        )
        .select_related(
            "reviewed_by",
        )
        .order_by(
            "-created_at",
        )
        if license_record
        else LicenseRenewalApplication.objects.none()
    )

    context = {
        "application": application,

        "license_record": license_record,

        "documents": documents,

        "renewal_history": renewal_history,
    }

    return render(
        request,
        "registrar/health_worker_record_detail.html",
        context,
    )