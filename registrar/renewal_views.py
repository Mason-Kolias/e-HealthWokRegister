
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Notification

from health_workers.models import (
    LicenseRenewalApplication,
    MedicalLicense,
)

from .license_pdf import generate_license_pdf


def registrar_required(request):
    return (
        request.user.is_authenticated
        and request.user.role == "registrar"
    )


def notify_health_worker(
    renewal,
    title,
    message,
    notification_type,
):
    Notification.objects.create(
        recipient=renewal.applicant,
        title=title,
        message=message,
        notification_type=notification_type,
        related_application=renewal.medical_license.application,
    )


# =========================================================
# RENEWAL APPLICATION LIST
# =========================================================

@login_required
def registrar_renewal_applications(request):

    if not registrar_required(request):
        return redirect("home")

    renewals = (
        LicenseRenewalApplication.objects
        .select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        )
        .exclude(status="draft")
        .order_by(
            "-submitted_at",
            "-created_at",
        )
    )

    pending_renewals = renewals.filter(
        status__in=[
            "submitted",
            "under_review",
        ]
    )

    approved_renewals = renewals.filter(
        status__in=[
            "approved",
            "renewed",
        ]
    )

    rejected_renewals = renewals.filter(
        status="rejected"
    )

    return render(
        request,
        "registrar/registrar_renewal_applications.html",
        {
            "renewals": renewals,
            "pending_renewals": pending_renewals,
            "approved_renewals": approved_renewals,
            "rejected_renewals": rejected_renewals,
        },
    )


# =========================================================
# REVIEW RENEWAL APPLICATION
# =========================================================

@login_required
def registrar_review_renewal(request, renewal_id):

    if not registrar_required(request):
        return redirect("home")

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
    )

    if renewal.status == "submitted":

        renewal.status = "under_review"

        renewal.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        notify_health_worker(
            renewal,
            "Renewal Application Under Review",
            (
                f"Your renewal application "
                f"{renewal.renewal_application_number} "
                f"is now under review by the registrar."
            ),
            "application_under_review",
        )

    return render(
        request,
        "registrar/review_renewal_application.html",
        {
            "renewal": renewal,
            "medical_license": renewal.medical_license,
            "application": renewal.medical_license.application,
        },
    )


# =========================================================
# APPROVE RENEWAL
# =========================================================
#
# IMPORTANT:
# Approval does NOT generate the renewed license.
#
# The renewal becomes "approved" and then appears in the
# separate Generate Renewed License page.
#
# =========================================================

@login_required
@require_POST
def approve_renewal(request, renewal_id):

    if not registrar_required(request):
        return redirect("home")

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
    )

    if renewal.status not in {
        "submitted",
        "under_review",
    }:

        messages.error(
            request,
            "This renewal application is no longer awaiting approval.",
        )

        return redirect(
            "registrar_review_renewal",
            renewal_id=renewal.id,
        )

    medical_license = renewal.medical_license

    if not medical_license:

        messages.error(
            request,
            "The medical license associated with this renewal could not be found.",
        )

        return redirect(
            "registrar_review_renewal",
            renewal_id=renewal.id,
        )

    renewal.status = "approved"
    renewal.reviewed_at = timezone.now()
    renewal.reviewed_by = request.user
    renewal.rejection_reason = ""

    renewal.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "updated_at",
        ]
    )

    notify_health_worker(
        renewal,
        "License Renewal Approved",
        (
            f"Your license renewal application "
            f"{renewal.renewal_application_number} "
            f"has been approved by the registrar. "
            f"Your renewed medical license is now being prepared."
        ),
        "application_approved",
    )

    messages.success(
        request,
        (
            "The renewal application has been approved. "
            "It is now ready for renewed license generation."
        ),
    )

    return redirect(
        "registrar_renewal_applications"
    )


# =========================================================
# REJECT RENEWAL
# =========================================================

@login_required
@require_POST
def reject_renewal(request, renewal_id):

    if not registrar_required(request):
        return redirect("home")

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
    )

    if renewal.status not in {
        "submitted",
        "under_review",
    }:

        messages.error(
            request,
            "This renewal application is no longer awaiting review.",
        )

        return redirect(
            "registrar_review_renewal",
            renewal_id=renewal.id,
        )

    rejection_reason = request.POST.get(
        "rejection_reason",
        "",
    ).strip()

    if not rejection_reason:

        messages.error(
            request,
            "Please provide a reason for rejecting the renewal application.",
        )

        return redirect(
            "registrar_review_renewal",
            renewal_id=renewal.id,
        )

    renewal.status = "rejected"
    renewal.rejection_reason = rejection_reason
    renewal.reviewed_at = timezone.now()
    renewal.reviewed_by = request.user

    renewal.save(
        update_fields=[
            "status",
            "rejection_reason",
            "reviewed_at",
            "reviewed_by",
            "updated_at",
        ]
    )

    notify_health_worker(
        renewal,
        "License Renewal Requires Correction",
        (
            f"Your renewal application "
            f"{renewal.renewal_application_number} "
            f"was not approved. "
            f"Reason: {rejection_reason}"
        ),
        "application_rejected",
    )

    messages.success(
        request,
        (
            "The renewal application has been rejected "
            "and the applicant has been notified."
        ),
    )

    return redirect(
        "registrar_renewal_applications"
    )


# =========================================================
# GENERATE RENEWED LICENSE PAGE
# =========================================================
#
# This is the separate page reached from:
#
# Generate Renewed License
#
# Only APPROVED renewals waiting for license generation
# are shown as ready to generate.
#
# Renewed records are also supplied so the template can
# display them if required.
#
# =========================================================

@login_required
def generate_renewed_licenses(request):

    if not registrar_required(request):
        return redirect("home")

    approved_renewals = (
        LicenseRenewalApplication.objects
        .select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        )
        .filter(
            status="approved"
        )
        .order_by(
            "-reviewed_at",
            "-created_at",
        )
    )

    renewed_renewals = (
        LicenseRenewalApplication.objects
        .select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        )
        .filter(
            status="renewed"
        )
        .order_by(
            "-reviewed_at",
            "-created_at",
        )
    )

    context = {
        "approved_renewals": approved_renewals,
        "renewed_renewals": renewed_renewals,
    }

    return render(
        request,
        "registrar/generate_renewed_licenses.html",
        context,
    )


# =========================================================
# GENERATE RENEWED LICENSE
# =========================================================
#
# This is intentionally separate from approve_renewal().
#
# The registrar clicks:
#
# Generate Renewed License
#
# The existing MedicalLicense record is updated.
#
# A NEW MedicalLicense record is NOT created.
#
# The existing license number remains unchanged.
#
# =========================================================

@login_required
@require_POST
def generate_renewed_license(request, renewal_id):

    if not registrar_required(request):
        return redirect("home")

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
    )

    if renewal.status != "approved":

        if renewal.status == "renewed":

            messages.info(
                request,
                "This renewal has already been generated.",
            )

        else:

            messages.error(
                request,
                (
                    "Only approved renewal applications "
                    "can have a renewed license generated."
                ),
            )

        return redirect(
            "generate_renewed_licenses"
        )

    medical_license = renewal.medical_license

    if not medical_license:

        messages.error(
            request,
            "The medical license associated with this renewal could not be found.",
        )

        return redirect(
            "generate_renewed_licenses"
        )

    application = medical_license.application

    # -----------------------------------------------------
    # Calculate new issue and expiry dates.
    # -----------------------------------------------------

    today = timezone.now().date()

    if today.month == 2 and today.day == 29:

        expiry_date = date(
            today.year + 1,
            2,
            28,
        )

    else:

        expiry_date = today + timedelta(
            days=365
        )

    # -----------------------------------------------------
    # Update the EXISTING medical license.
    #
    # The license number remains unchanged.
    # -----------------------------------------------------

    medical_license.issue_date = today
    medical_license.expiry_date = expiry_date
    medical_license.status = "active"

    # -----------------------------------------------------
    # Generate the renewed PDF using the existing PDF
    # generator.
    #
    # This uses the same argument names already used by
    # generate_medical_license() in registrar/views.py.
    # -----------------------------------------------------

    try:

        pdf_buffer = generate_license_pdf(
            application=application,
            license_record=medical_license,
        )

        pdf_content = pdf_buffer.getvalue()

        medical_license.license_document.save(
            f"{medical_license.license_number}.pdf",
            ContentFile(pdf_content),
            save=False,
        )

        medical_license.save()

    except Exception:

        messages.error(
            request,
            (
                "The renewed medical license could not be generated. "
                "Please check the license PDF configuration and try again."
            ),
        )

        return redirect(
            "generate_renewed_licenses"
        )

    # -----------------------------------------------------
    # Mark the renewal as fully renewed only AFTER the
    # license PDF has been generated successfully.
    # -----------------------------------------------------

    renewal.status = "renewed"
    renewal.reviewed_at = timezone.now()
    renewal.reviewed_by = request.user
    renewal.rejection_reason = ""

    renewal.save(
        update_fields=[
            "status",
            "reviewed_at",
            "reviewed_by",
            "rejection_reason",
            "updated_at",
        ]
    )

    # -----------------------------------------------------
    # Notify the health worker.
    # -----------------------------------------------------

    notify_health_worker(
        renewal,
        "Renewed Medical License Available",
        (
            f"Your license renewal application "
            f"{renewal.renewal_application_number} "
            f"has been completed. Your medical license "
            f"{medical_license.license_number} has been renewed "
            f"until "
            f"{medical_license.expiry_date.strftime('%d %B %Y')}."
        ),
        "application_approved",
    )

    messages.success(
        request,
        (
            f"The renewed medical license for "
            f"{renewal.applicant.get_full_name() or renewal.applicant.username} "
            f"has been generated successfully."
        ),
    )

    return redirect(
        "generate_renewed_licenses"
    )
