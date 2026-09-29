from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import Notification

from .models import (
    LicenseRenewalApplication,
    MedicalLicense,
)

from .renewal_forms import LicenseRenewalApplicationForm

from .views import create_health_worker_notification


User = get_user_model()


# =========================================================
# GET RENEWABLE MEDICAL LICENSE
# =========================================================

def get_renewable_medical_license(user):

    return (
        MedicalLicense.objects
        .filter(
            applicant=user,
            status__in=[
                "active",
                "expired",
            ],
        )
        .select_related(
            "application",
        )
        .order_by(
            "-expiry_date",
        )
        .first()
    )


# =========================================================
# NOTIFY REGISTRARS
# =========================================================
"""   
def notify_registrars(renewal):

    registrars = User.objects.filter(
        role="registrar",
        is_active=True,
    )

    for registrar in registrars:

        Notification.objects.create(
            recipient=registrar,
            title="New License Renewal Application",
            message=(
                f"{renewal.applicant.get_full_name() or renewal.applicant.username} "
                f"has submitted license renewal application "
                f"{renewal.renewal_application_number}."
            ),
            notification_type="application_submitted",
            related_application=(
                renewal.medical_license.application
            ),
        )
"""

def notify_registrars(renewal):

    registrars = User.objects.filter(
        role="registrar",
        is_active=True,
    )

    for registrar in registrars:

        Notification.objects.create(
            recipient=registrar,
            title="New License Renewal Application",
            message=(
                f"{renewal.applicant.get_full_name() or renewal.applicant.username} "
                f"has submitted license renewal application "
                f"{renewal.renewal_application_number}."
            ),
            notification_type="application_submitted",
            related_renewal=renewal,
        )
     

# =========================================================
# ANNUAL LICENSE RENEWAL
# =========================================================

@login_required
def license_renewal_application(request):

    if request.user.role != "health_worker":

        return redirect(
            "home"
        )

    medical_license = get_renewable_medical_license(
        request.user
    )

    existing_renewal = None

    if medical_license:

        existing_renewal = (
            LicenseRenewalApplication.objects
            .filter(
                applicant=request.user,
                medical_license=medical_license,
            )
            .order_by(
                "-created_at",
            )
            .first()
        )

    # =====================================================
    # EXISTING SUBMITTED / UNDER REVIEW / APPROVED / RENEWED
    #
    # Keep the renewal page accessible so the health worker
    # can see the current renewal status.
    # =====================================================

    if existing_renewal:

        if existing_renewal.status in {
            "submitted",
            "under_review",
            "approved",
            "renewed",
        }:

            today = timezone.now().date()

            days_until_expiry = None

            if medical_license:

                days_until_expiry = (
                    medical_license.expiry_date
                    - today
                ).days

            return render(
                request,
                "health_workers/license_renewal.html",
                {
                    "form": None,
                    "medical_license": medical_license,
                    "renewal": existing_renewal,
                    "days_until_expiry": days_until_expiry,
                },
            )

    # =====================================================
    # REJECTED APPLICATION
    #
    # Allow the applicant to correct and resubmit.
    # =====================================================

    renewal = None

    if existing_renewal:

        if existing_renewal.status == "rejected":

            renewal = existing_renewal

            renewal.status = "draft"
            renewal.rejection_reason = ""

            renewal.save(
                update_fields=[
                    "status",
                    "rejection_reason",
                    "updated_at",
                ]
            )

    # =====================================================
    # SUBMIT / SAVE RENEWAL FORM
    # =====================================================

    if request.method == "POST":

        if not medical_license:

            messages.error(
                request,
                (
                    "You do not have a medical license "
                    "available for renewal."
                ),
            )

            return redirect(
                "license_renewal_application"
            )

        if medical_license.status not in {
            "active",
            "expired",
        }:

            messages.error(
                request,
                (
                    "Your medical license cannot be renewed "
                    "because it is not active or expired."
                ),
            )

            return redirect(
                "license_renewal_application"
            )

        form = LicenseRenewalApplicationForm(
            request.POST,
            request.FILES,
            instance=renewal,
            applicant=request.user,
        )

        if form.is_valid():

            renewal = form.save(
                commit=False
            )

            renewal.applicant = request.user
            renewal.medical_license = (
                form.validated_medical_license
            )
            renewal.status = "draft"

            renewal.save()

            return redirect(
                "review_renewal_application",
                renewal_id=renewal.id,
            )

    else:

        initial = {}

        if medical_license:

            initial = {
                "registration_number": (
                    medical_license.license_number
                ),
                "current_employer": (
                    medical_license.application.current_employer
                    or ""
                ),
                "current_work_location": (
                    medical_license.application.residential_address
                    or ""
                ),
                "contact_phone": (
                    medical_license.application.phone_number
                    or ""
                ),
                "email": (
                    medical_license.application.email
                    or request.user.email
                    or ""
                ),
            }

        form = LicenseRenewalApplicationForm(
            instance=renewal,
            applicant=request.user,
            initial=initial,
        )

    # =====================================================
    # EXPIRY INFORMATION
    # =====================================================

    today = timezone.now().date()

    days_until_expiry = None

    if medical_license:

        days_until_expiry = (
            medical_license.expiry_date
            - today
        ).days

    return render(
        request,
        "health_workers/license_renewal.html",
        {
            "form": form,
            "medical_license": medical_license,
            "renewal": renewal,
            "days_until_expiry": days_until_expiry,
        },
    )


# =========================================================
# REVIEW RENEWAL APPLICATION
# =========================================================

@login_required
def review_renewal_application(
    request,
    renewal_id,
):

    if request.user.role != "health_worker":

        return redirect(
            "home"
        )

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
        applicant=request.user,
    )

    if renewal.status != "draft":

        messages.error(
            request,
            "This renewal application cannot be reviewed.",
        )

        return redirect(
            "license_renewal_application"
        )

    medical_license = renewal.medical_license

    if not medical_license:

        messages.error(
            request,
            "The medical license connected to this renewal could not be found.",
        )

        return redirect(
            "license_renewal_application"
        )

    if medical_license.status not in {
        "active",
        "expired",
    }:

        messages.error(
            request,
            (
                "This medical license cannot be renewed "
                "because it is not active or expired."
            ),
        )

        return redirect(
            "license_renewal_application"
        )

    return render(
        request,
        "health_workers/review_renewal_application.html",
        {
            "renewal": renewal,
            "medical_license": medical_license,
            "application": (
                medical_license.application
            ),
        },
    )


# =========================================================
# SUBMIT RENEWAL APPLICATION
# =========================================================


@login_required
@require_POST
def submit_renewal_application(
    request,
    renewal_id,
):

    # =====================================================
    # HEALTH WORKER ONLY
    # =====================================================

    if request.user.role != "health_worker":

        return redirect(
            "home"
        )

    # =====================================================
    # GET THE RENEWAL
    #
    # IMPORTANT:
    # Do NOT filter status="draft" here.
    #
    # We first retrieve the renewal and then decide whether
    # it may be submitted. This prevents a 404 when the
    # health worker accidentally clicks Submit twice.
    # =====================================================

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "medical_license",
            "medical_license__application",
        ),
        id=renewal_id,
        applicant=request.user,
    )

    # =====================================================
    # ALREADY SUBMITTED / LOCKED
    # =====================================================

    if renewal.status in {
        "submitted",
        "under_review",
        "approved",
        "renewed",
    }:

        messages.info(
            request,
            (
                "This renewal application has already been "
                "submitted and is currently locked."
            ),
        )

        return redirect(
            "license_renewal_application"
        )

    # =====================================================
    # REJECTED APPLICATION
    #
    # A rejected renewal may be corrected.
    # =====================================================

    if renewal.status == "rejected":

        renewal.status = "draft"

        renewal.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

    # =====================================================
    # ONLY DRAFT APPLICATIONS MAY BE SUBMITTED
    # =====================================================

    if renewal.status != "draft":

        messages.error(
            request,
            "This renewal application cannot be submitted.",
        )

        return redirect(
            "license_renewal_application"
        )

    # =====================================================
    # GET MEDICAL LICENSE
    # =====================================================

    medical_license = renewal.medical_license

    if not medical_license:

        messages.error(
            request,
            "Your medical license could not be found.",
        )

        return redirect(
            "license_renewal_application"
        )

    # =====================================================
    # VERIFY OWNERSHIP
    # =====================================================

    if medical_license.applicant_id != request.user.id:

        messages.error(
            request,
            "This license does not belong to your account.",
        )

        return redirect(
            "license_renewal_application"
        )

    # =====================================================
    # ACTIVE OR EXPIRED LICENSES MAY BE RENEWED
    # =====================================================

    if medical_license.status not in {
        "active",
        "expired",
    }:

        messages.error(
            request,
            (
                "This medical license cannot be renewed "
                "because it is not active or expired."
            ),
        )

        return redirect(
            "license_renewal_application"
        )

    # =====================================================
    # PAYMENT RECEIPT REQUIRED
    # =====================================================

    if not renewal.payment_receipt:

        messages.error(
            request,
            "Please upload your renewal fee receipt.",
        )

        return redirect(
            "review_renewal_application",
            renewal_id=renewal.id,
        )

    # =====================================================
    # DECLARATION REQUIRED
    # =====================================================

    if not request.POST.get("declaration"):

        messages.error(
            request,
            "Please confirm the declaration before submitting.",
        )

        return redirect(
            "review_renewal_application",
            renewal_id=renewal.id,
        )

    # =====================================================
    # SUBMIT AND LOCK
    # =====================================================

    renewal.status = "submitted"
    renewal.submitted_at = timezone.now()
    renewal.rejection_reason = ""

    renewal.save(
        update_fields=[
            "status",
            "submitted_at",
            "rejection_reason",
            "updated_at",
        ]
    )

    # =====================================================
    # NOTIFY REGISTRARS
    # =====================================================

    notify_registrars(
        renewal
    )

    # =====================================================
    # NOTIFY HEALTH WORKER
    # =====================================================

    Notification.objects.create(
        recipient=request.user,
        title="Renewal Application Submitted",
        message=(
            f"Your license renewal application "
            f"{renewal.renewal_application_number} "
            f"has been submitted successfully and is "
            f"awaiting registrar review."
        ),
        notification_type="application_submitted",
        related_renewal=renewal,
    )

    # =====================================================
    # SUCCESS MESSAGE
    # =====================================================

    messages.success(
        request,
        (
            "Your license renewal application has been "
            "submitted successfully. The application is "
            "now locked while it is being reviewed."
        ),
    )

    return redirect(
        "license_renewal_application"
    )

# =========================================================
# DOWNLOAD RENEWED LICENSE
# =========================================================

@login_required
def download_renewed_license(
    request,
    renewal_id,
):

    if request.user.role != "health_worker":

        return redirect(
            "home"
        )

    renewal = get_object_or_404(
        LicenseRenewalApplication.objects.select_related(
            "medical_license",
        ),
        id=renewal_id,
        applicant=request.user,
        status="renewed",
    )

    medical_license = renewal.medical_license

    if not medical_license:

        messages.error(
            request,
            "Your renewed medical license could not be found.",
        )

        return redirect(
            "health_worker_dashboard"
        )

    if not medical_license.license_document:

        messages.error(
            request,
            "Your renewed license document is not available yet.",
        )

        return redirect(
            "license_renewal_application"
        )

    response = FileResponse(
        medical_license.license_document.open("rb"),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'attachment; '
        f'filename="{medical_license.license_number}.pdf"'
    )

    return response
