from copy import copy
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Count
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from openpyxl import Workbook

from accounts.models import Notification

from health_workers.models import (
    LicenseRenewalApplication,
    MedicalLicense,
    MedicalLicenseApplication,
)

from .license_pdf import generate_license_pdf

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def create_notification(
    recipient,
    title,
    message,
    notification_type="general",
    application=None,
):
    if not recipient:
        return

    Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        related_application=application,
    )


def get_notification_context(user):
    notifications = (
        Notification.objects
        .filter(recipient=user)
        .order_by("-created_at")[:10]
    )

    unread_notifications = (
        Notification.objects
        .filter(
            recipient=user,
            is_read=False,
        )
        .count()
    )

    return {
        "notifications": notifications,
        "unread_notifications": unread_notifications,
        "notification_count": unread_notifications,
    }

"""     
@login_required
def registrar_dashboard(request):

    if request.user.role != "registrar":
        return redirect("home")

    total_applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
        .count()
    )

    pending_review = (
        MedicalLicenseApplication.objects
        .filter(
            status__in=[
                "submitted",
                "under_review",
            ]
        )
        .count()
    )

    approved_applications = (
        MedicalLicenseApplication.objects
        .filter(
            status__in=[
                "approved",
                "license_generated",
            ]
        )
        .count()
    )

    rejected_applications = (
        MedicalLicenseApplication.objects
        .filter(status="rejected")
        .count()
    )

    licenses_issued = MedicalLicense.objects.count()

    new_applications = (
        MedicalLicenseApplication.objects
        .filter(application_type="new")
        .exclude(status="draft")
        .count()
    )

    under_review = (
        MedicalLicenseApplication.objects
        .filter(status="under_review")
        .count()
    )

    approved = (
        MedicalLicenseApplication.objects
        .filter(
            status__in=[
                "approved",
                "license_generated",
            ]
        )
        .count()
    )

    denominator = total_applications or 1

    new_applications_percentage = min(
        round(
            (new_applications / denominator) * 100
        ),
        100,
    )

    under_review_percentage = min(
        round(
            (under_review / denominator) * 100
        ),
        100,
    )

    approved_percentage = min(
        round(
            (approved / denominator) * 100
        ),
        100,
    )

    # License renewal statistics

    total_renewals = (
        LicenseRenewalApplication.objects
        .exclude(status="draft")
        .count()
    )

    pending_renewals = (
        LicenseRenewalApplication.objects
        .filter(
            status__in=[
                "submitted",
                "under_review",
            ]
        )
        .count()
    )

    under_review_renewals = (
        LicenseRenewalApplication.objects
        .filter(status="under_review")
        .count()
    )

    renewed_licenses = (
        LicenseRenewalApplication.objects
        .filter(status="renewed")
        .count()
    )

    approved_renewals = (
        LicenseRenewalApplication.objects
        .filter(status="approved")
        .count()
    )

    rejected_renewals = (
        LicenseRenewalApplication.objects
        .filter(status="rejected")
        .count()
    )

    recent_renewals = (
        LicenseRenewalApplication.objects
        .select_related(
            "applicant",
            "medical_license",
        )
        .exclude(status="draft")
        .order_by(
            "-submitted_at",
            "-created_at",
        )[:5]
    )

    context = {
        "total_applications":
            total_applications,

        "pending_review":
            pending_review,

        "approved_applications":
            approved_applications,

        "rejected_applications":
            rejected_applications,

        "licenses_issued":
            licenses_issued,

        "new_applications_percentage":
            new_applications_percentage,

        "under_review_percentage":
            under_review_percentage,

        "approved_percentage":
            approved_percentage,

        "total_renewals":
            total_renewals,

        "pending_renewals":
            pending_renewals,

        "under_review_renewals":
            under_review_renewals,

        "approved_renewals":
            approved_renewals,

        "renewed_licenses":
            renewed_licenses,

        "rejected_renewals":
            rejected_renewals,

        "recent_renewals":
            recent_renewals,

        **get_notification_context(
            request.user
        ),
    }

    return render(
        request,
        "registrar/registrar_dashboard.html",
        context,
    )

  """
@login_required
def registrar_dashboard(request):

    if request.user.role != "registrar":
        return redirect("home")

    # =====================================================
    # NEW LICENSE APPLICATION STATISTICS
    # =====================================================

    new_license_applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
    )

    total_new_applications = (
        new_license_applications.count()
    )

    pending_new_applications = (
        new_license_applications
        .filter(
            status__in=[
                "submitted",
                "under_review",
            ]
        )
        .count()
    )

    approved_new_applications = (
        new_license_applications
        .filter(
            status__in=[
                "approved",
                "license_generated",
            ]
        )
        .count()
    )

    rejected_new_applications = (
        new_license_applications
        .filter(
            status="rejected"
        )
        .count()
    )


    # =====================================================
    # LICENSE RENEWAL STATISTICS
    # =====================================================

    renewal_applications = (
        LicenseRenewalApplication.objects
        .exclude(status="draft")
    )

    total_renewals = (
        renewal_applications.count()
    )

    pending_renewals = (
        renewal_applications
        .filter(
            status__in=[
                "submitted",
                "under_review",
            ]
        )
        .count()
    )

    under_review_renewals = (
        renewal_applications
        .filter(
            status="under_review"
        )
        .count()
    )

    approved_renewals = (
        renewal_applications
        .filter(
            status="approved"
        )
        .count()
    )

    renewed_licenses = (
        renewal_applications
        .filter(
            status="renewed"
        )
        .count()
    )

    rejected_renewals = (
        renewal_applications
        .filter(
            status="rejected"
        )
        .count()
    )


    # =====================================================
    # COMBINED DASHBOARD STATISTICS
    #
    # Main dashboard cards represent BOTH:
    #   1. New license applications
    #   2. License renewal applications
    # =====================================================

    total_applications = (
        total_new_applications
        + total_renewals
    )

    pending_review = (
        pending_new_applications
        + pending_renewals
    )

    approved_applications = (
        approved_new_applications
        + approved_renewals
        + renewed_licenses
    )

    rejected_applications = (
        rejected_new_applications
        + rejected_renewals
    )


    # =====================================================
    # LICENSES ISSUED
    #
    # MedicalLicense represents the actual license record.
    # A renewed license updates the existing record, so it
    # should NOT create an additional MedicalLicense count.
    # =====================================================

    licenses_issued = (
        MedicalLicense.objects.count()
    )


    # =====================================================
    # APPLICATION STATISTICS
    # =====================================================

    new_applications = (
        MedicalLicenseApplication.objects
        .filter(
            application_type="new"
        )
        .exclude(
            status="draft"
        )
        .count()
    )

    under_review_new = (
        MedicalLicenseApplication.objects
        .filter(
            status="under_review"
        )
        .count()
    )

    under_review_total = (
        under_review_new
        + under_review_renewals
    )

    approved_total = (
        approved_new_applications
        + approved_renewals
        + renewed_licenses
    )


    # =====================================================
    # PERCENTAGES
    # =====================================================

    denominator = (
        total_applications or 1
    )

    new_applications_percentage = min(
        round(
            (
                new_applications
                / denominator
            )
            * 100
        ),
        100,
    )

    under_review_percentage = min(
        round(
            (
                under_review_total
                / denominator
            )
            * 100
        ),
        100,
    )

    approved_percentage = min(
        round(
            (
                approved_total
                / denominator
            )
            * 100
        ),
        100,
    )


    # =====================================================
    # RECENT RENEWALS
    # =====================================================

    recent_renewals = (
        LicenseRenewalApplication.objects
        .select_related(
            "applicant",
            "medical_license",
        )
        .exclude(
            status="draft"
        )
        .order_by(
            "-submitted_at",
            "-created_at",
        )[:5]
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        # -------------------------------------------------
        # MAIN DASHBOARD CARDS
        # -------------------------------------------------

        "total_applications":
            total_applications,

        "pending_review":
            pending_review,

        "approved_applications":
            approved_applications,

        "rejected_applications":
            rejected_applications,

        "licenses_issued":
            licenses_issued,


        # -------------------------------------------------
        # APPLICATION STATISTICS
        # -------------------------------------------------

        "new_applications_percentage":
            new_applications_percentage,

        "under_review_percentage":
            under_review_percentage,

        "approved_percentage":
            approved_percentage,


        # -------------------------------------------------
        # RENEWAL STATISTICS
        # -------------------------------------------------

        "total_renewals":
            total_renewals,

        "pending_renewals":
            pending_renewals,

        "under_review_renewals":
            under_review_renewals,

        "approved_renewals":
            approved_renewals,

        "renewed_licenses":
            renewed_licenses,

        "rejected_renewals":
            rejected_renewals,

        "recent_renewals":
            recent_renewals,


        # -------------------------------------------------
        # NOTIFICATIONS
        # -------------------------------------------------

        **get_notification_context(
            request.user
        ),
    }


    # =====================================================
    # RENDER DASHBOARD
    # =====================================================

    return render(
        request,
        "registrar/registrar_dashboard.html",
        context,
    )
  
@login_required
def registrar_review_applications(request):

    if request.user.role != "registrar":
        return redirect("home")

    applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
        .select_related("applicant")
        .order_by(
            "-submitted_at",
            "-created_at",
        )
    )

    context = {
        "applications":
            applications,
    }

    context.update(
        get_notification_context(
            request.user
        )
    )

    return render(
        request,
        "registrar/review_applications.html",
        context,
    )


@login_required
def registrar_review_application(
    request,
    application_id,
):

    if request.user.role != "registrar":
        return redirect("home")

    application = get_object_or_404(
        MedicalLicenseApplication.objects
        .select_related("applicant"),
        id=application_id,
    )

    if application.status == "draft":

        messages.error(
            request,
            "This application has not been submitted.",
        )

        return redirect(
            "registrar_review_applications"
        )

    if (
        request.method == "GET"
        and application.status == "submitted"
    ):

        application.status = "under_review"

        application.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        create_notification(
            recipient=application.applicant,
            title="Application Under Review",
            message=(
                f"Your medical license application "
                f"{application.application_number} "
                f"is now under review by the Registrar."
            ),
            notification_type="application_under_review",
            application=application,
        )

    if request.method == "POST":

        action = request.POST.get("action")

        if application.status != "under_review":

            messages.error(
                request,
                "This application is no longer available "
                "for a Registrar decision.",
            )

            return redirect(
                "registrar_review_applications"
            )

        if action == "approve":

            application.status = "approved"
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.rejection_reason = ""

            application.save()

            create_notification(
                recipient=application.applicant,
                title="Application Approved",
                message=(
                    f"Your medical license application "
                    f"{application.application_number} "
                    f"has been approved successfully. "
                    f"Your medical license can now be "
                    f"generated by the Registrar."
                ),
                notification_type="application_approved",
                application=application,
            )

            messages.success(
                request,
                (
                    f"Application "
                    f"{application.application_number} "
                    f"has been approved successfully."
                ),
            )

            return redirect(
                "registrar_review_applications"
            )

        if action == "reject":

            rejection_reason = request.POST.get(
                "rejection_reason",
                "",
            ).strip()

            if not rejection_reason:

                messages.error(
                    request,
                    "Please provide a reason for rejecting "
                    "this application.",
                )

                return redirect(
                    "registrar_review_application",
                    application_id=application.id,
                )

            application.status = "rejected"
            application.reviewed_at = timezone.now()
            application.reviewed_by = request.user
            application.rejection_reason = (
                rejection_reason
            )

            application.save()

            create_notification(
                recipient=application.applicant,
                title="Application Rejected",
                message=(
                    f"Your medical license application "
                    f"{application.application_number} "
                    f"has been rejected.\n\n"
                    f"Reason: {rejection_reason}"
                ),
                notification_type="application_rejected",
                application=application,
            )

            messages.success(
                request,
                (
                    f"Application "
                    f"{application.application_number} "
                    f"has been rejected."
                ),
            )

            return redirect(
                "registrar_review_applications"
            )

    documents = (
        application.documents
        .all()
        .order_by("document_type")
    )

    context = {
        "application":
            application,

        "documents":
            documents,
    }

    context.update(
        get_notification_context(
            request.user
        )
    )

    return render(
        request,
        "registrar/review_application.html",
        context,
    )


@login_required
def generate_license_page(request):

    if request.user.role != "registrar":
        return redirect("home")

    approved_applications = (
        MedicalLicenseApplication.objects
        .filter(status="approved")
        .select_related("applicant")
        .order_by(
            "-reviewed_at",
            "-created_at",
        )
    )

    context = {
        "approved_applications":
            approved_applications,
    }

    context.update(
        get_notification_context(
            request.user
        )
    )

    return render(
        request,
        "registrar/generate_license.html",
        context,
    )


@login_required
def generate_medical_license(
    request,
    application_id,
):

    if request.user.role != "registrar":

        messages.error(
            request,
            "You are not authorized to generate medical licenses.",
        )

        return redirect("home")

    if request.method != "POST":

        messages.error(
            request,
            "Invalid request.",
        )

        return redirect(
            "generate_license_page"
        )

    application = get_object_or_404(
        MedicalLicenseApplication,
        id=application_id,
    )

    if application.status != "approved":

        messages.error(
            request,
            "Only approved applications can receive a medical license.",
        )

        return redirect(
            "generate_license_page"
        )

    existing_license = getattr(
        application,
        "license",
        None,
    )

    if existing_license:

        messages.warning(
            request,
            "A medical license has already been generated "
            "for this application.",
        )

        return redirect(
            "generate_license_page"
        )

    issue_date = timezone.localdate()

    try:

        expiry_date = issue_date.replace(
            year=issue_date.year + 1
        )

    except ValueError:

        expiry_date = issue_date.replace(
            year=issue_date.year + 1,
            month=2,
            day=28,
        )

    year = issue_date.year

    last_license = (
        MedicalLicense.objects
        .filter(
            license_number__startswith=(
                f"PNG-MED-{year}-"
            )
        )
        .order_by("-id")
        .first()
    )

    if last_license:

        try:

            last_number = int(
                last_license.license_number
                .split("-")[-1]
            )

            next_number = last_number + 1

        except (
            ValueError,
            IndexError,
        ):

            next_number = 1

    else:

        next_number = 1

    license_number = (
        f"PNG-MED-{year}-{next_number:06d}"
    )

    license_record = MedicalLicense.objects.create(
        application=application,
        applicant=application.applicant,
        license_number=license_number,
        issue_date=issue_date,
        expiry_date=expiry_date,
        status="active",
    )

    try:

        pdf_buffer = generate_license_pdf(
            application=application,
            license_record=license_record,
        )

        license_record.license_document.save(
            f"{license_number}.pdf",
            ContentFile(
                pdf_buffer.getvalue()
            ),
            save=True,
        )

    except Exception:

        license_record.delete()

        messages.error(
            request,
            "The medical license could not be generated. "
            "Please try again.",
        )

        return redirect(
            "generate_license_page"
        )

    application.status = "license_generated"

    application.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    create_notification(
        recipient=application.applicant,
        title="Medical License Generated",
        message=(
            f"Your medical license {license_number} "
            f"has been generated successfully. You can now "
            f"download your digital medical license from "
            f"your Health Worker Dashboard."
        ),
        notification_type="license_generated",
        application=application,
    )

    messages.success(
        request,
        (
            f"Medical license {license_number} "
            f"has been successfully generated for "
            f"{application.full_name}."
        ),
    )

    return redirect(
        "generate_license_page"
    )


@login_required
def download_medical_license(
    request,
    application_id,
):

    if request.user.role != "health_worker":
        return redirect("home")

    application = get_object_or_404(
        MedicalLicenseApplication,
        id=application_id,
        applicant=request.user,
        status="license_generated",
    )

    license_record = getattr(
        application,
        "license",
        None,
    )

    if not license_record:

        messages.error(
            request,
            "A medical license record could not be found.",
        )

        return redirect(
            "health_worker_dashboard"
        )

    if not license_record.license_document:

        messages.error(
            request,
            "The medical license document is not available.",
        )

        return redirect(
            "health_worker_dashboard"
        )

    try:

        file_handle = (
            license_record
            .license_document
            .open("rb")
        )

    except FileNotFoundError:

        messages.error(
            request,
            "The medical license PDF file could not be found. "
            "Please contact the Registrar to regenerate the license.",
        )

        return redirect(
            "health_worker_dashboard"
        )

    return FileResponse(
        file_handle,
        as_attachment=True,
        filename=(
            f"{license_record.license_number}.pdf"
        ),
    )


@login_required
def registrar_reports(request):

    if request.user.role != "registrar":
        return redirect("home")

    applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
    )

    renewals = (
        LicenseRenewalApplication.objects
        .exclude(status="draft")
    )

    selected_year = request.GET.get(
        "year",
        "all",
    )

    selected_profession = request.GET.get(
        "profession",
        "",
    )

    selected_province = request.GET.get(
        "province",
        "",
    )

    selected_workplace_province = request.GET.get(
        "workplace_province",
        "",
    )

    selected_application_type = request.GET.get(
        "application_type",
        "",
    )

    if (
        selected_year
        and selected_year != "all"
    ):

        try:

            year_value = int(
                selected_year
            )

            applications = applications.filter(
                created_at__year=year_value
            )

            renewals = renewals.filter(
                created_at__year=year_value
            )

        except ValueError:

            selected_year = "all"

    if selected_profession:

        applications = applications.filter(
            profession=selected_profession
        )

    if selected_province:

        applications = applications.filter(
            province=selected_province
        )

    if selected_workplace_province:

        applications = applications.filter(
            workplace_province=(
                selected_workplace_province
            )
        )

    if selected_application_type:

        applications = applications.filter(
            application_type=(
                selected_application_type
            )
        )

    total_applications = applications.count()

    submitted_applications = applications.filter(
        status="submitted"
    ).count()

    under_review_applications = applications.filter(
        status="under_review"
    ).count()

    approved_applications = applications.filter(
        status="approved"
    ).count()

    rejected_applications = applications.filter(
        status="rejected"
    ).count()

    licenses_issued = (
        MedicalLicense.objects
        .filter(
            application__in=applications
        )
        .count()
    )

    active_licenses = (
        MedicalLicense.objects
        .filter(
            application__in=applications,
            status="active",
        )
        .count()
    )

    registered_workers = applications.filter(
        status__in=[
            "approved",
            "license_generated",
        ]
    ).count()

    pending_applications = applications.filter(
        status__in=[
            "submitted",
            "under_review",
        ]
    ).count()

    # Renewal statistics

    total_renewals = renewals.count()

    pending_renewals = renewals.filter(
        status__in=[
            "submitted",
            "under_review",
        ]
    ).count()

    under_review_renewals = renewals.filter(
        status="under_review"
    ).count()

    renewed_licenses = renewals.filter(
        status="renewed"
    ).count()

    rejected_renewals = renewals.filter(
        status="rejected"
    ).count()

    status_names = {
        "submitted": "Submitted",
        "under_review": "Under Review",
        "approved": "Approved",
        "rejected": "Rejected",
        "license_generated": "License Generated",
    }

    status_queryset = (
        applications
        .values("status")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    status_data = []

    for item in status_queryset:

        status_value = item.get("status")

        display_name = status_names.get(
            status_value,
            (
                (status_value or "Unknown")
                .replace("_", " ")
                .title()
            ),
        )

        status_data.append({
            "status":
                status_value or "",

            "display_name":
                display_name,

            "total":
                item["total"],
        })

    renewal_status_names = {
        "submitted": "Submitted",
        "under_review": "Under Review",
        "approved": "Approved",
        "rejected": "Rejected",
        "renewed": "Renewed",
    }

    renewal_status_queryset = (
        renewals
        .values("status")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    renewal_status_data = []

    for item in renewal_status_queryset:

        status_value = item.get("status")

        renewal_status_data.append({
            "status":
                status_value or "",

            "display_name":
                renewal_status_names.get(
                    status_value,
                    (
                        (status_value or "Unknown")
                        .replace("_", " ")
                        .title()
                    ),
                ),

            "total":
                item["total"],
        })

    registered_applications = applications.filter(
        status__in=[
            "approved",
            "license_generated",
        ]
    )

    profession_queryset = (
        registered_applications
        .values("profession")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    profession_data = []

    for item in profession_queryset:

        value = item.get("profession")

        if value:

            display_name = (
                value
                .replace("_", " ")
                .title()
            )

        else:

            display_name = "Not Specified"

        profession_data.append({
            "profession":
                value or "",

            "display_name":
                display_name,

            "total":
                item["total"],
        })

    province_queryset = (
        registered_applications
        .values("province")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    province_data = []

    for item in province_queryset:

        value = item.get("province")

        province_data.append({
            "province":
                value or "Not Specified",

            "total":
                item["total"],
        })

    workplace_province_queryset = (
        registered_applications
        .values("workplace_province")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    workplace_province_data = []

    for item in workplace_province_queryset:

        value = item.get(
            "workplace_province"
        )

        workplace_province_data.append({
            "workplace_province":
                value or "Not Specified",

            "total":
                item["total"],
        })

    qualification_data = (
        registered_applications
        .values("qualification")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    institution_data = (
        registered_applications
        .values("institution")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    graduate_data = (
        registered_applications
        .filter(
            year_completed__isnull=False
        )
        .values("year_completed")
        .annotate(total=Count("id"))
        .order_by("year_completed")
    )

    application_type_queryset = (
        applications
        .values("application_type")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    application_type_data = []

    for item in application_type_queryset:

        value = item.get(
            "application_type"
        )

        application_type_data.append({
            "application_type":
                value or "Not Specified",

            "display_name": (
                value
                .replace("_", " ")
                .title()
                if value
                else "Not Specified"
            ),

            "total":
                item["total"],
        })

    month_names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    monthly_data = []

    if selected_year != "all":

        try:

            report_year = int(
                selected_year
            )

            for month_number in range(
                1,
                13,
            ):

                total = applications.filter(
                    created_at__year=report_year,
                    created_at__month=month_number,
                ).count()

                monthly_data.append({
                    "label":
                        month_names[
                            month_number - 1
                        ],

                    "short_label":
                        month_names[
                            month_number - 1
                        ][:3],

                    "total":
                        total,
                })

        except ValueError:

            monthly_data = []

    else:

        today = timezone.localdate()

        for offset in range(
            11,
            -1,
            -1,
        ):

            month_index = (
                today.month - offset
            )

            year_value = today.year

            while month_index <= 0:

                month_index += 12
                year_value -= 1

            total = applications.filter(
                created_at__year=year_value,
                created_at__month=month_index,
            ).count()

            monthly_data.append({
                "label": (
                    f"{month_names[month_index - 1]} "
                    f"{year_value}"
                ),

                "short_label": (
                    f"{month_names[month_index - 1][:3]} "
                    f"{str(year_value)[-2:]}"
                ),

                "total":
                    total,
            })

    monthly_new_data = []
    monthly_renewal_data = []

    for item in monthly_data:

        if selected_year != "all":

            try:

                month_number = (
                    month_names.index(
                        item["label"]
                    ) + 1
                )

                report_year = int(
                    selected_year
                )

                new_total = applications.filter(
                    created_at__year=report_year,
                    created_at__month=month_number,
                    application_type="new",
                ).count()

                renewal_total = renewals.filter(
                    created_at__year=report_year,
                    created_at__month=month_number,
                ).count()

            except (
                ValueError,
                TypeError,
            ):

                new_total = 0
                renewal_total = 0

        else:

            parts = item["label"].split()

            try:

                month_number = (
                    month_names.index(
                        parts[0]
                    ) + 1
                )

                year_value = int(
                    parts[1]
                )

                new_total = applications.filter(
                    created_at__year=year_value,
                    created_at__month=month_number,
                    application_type="new",
                ).count()

                renewal_total = renewals.filter(
                    created_at__year=year_value,
                    created_at__month=month_number,
                ).count()

            except (
                ValueError,
                IndexError,
            ):

                new_total = 0
                renewal_total = 0

        monthly_new_data.append(
            new_total
        )

        monthly_renewal_data.append(
            renewal_total
        )

    license_monthly_data = []

    if selected_year != "all":

        try:

            report_year = int(
                selected_year
            )

            for month_number in range(
                1,
                13,
            ):

                total = (
                    MedicalLicense.objects
                    .filter(
                        application__in=applications,
                        issue_date__year=report_year,
                        issue_date__month=month_number,
                    )
                    .count()
                )

                license_monthly_data.append(
                    total
                )

        except ValueError:

            license_monthly_data = []

    else:

        today = timezone.localdate()

        for offset in range(
            11,
            -1,
            -1,
        ):

            month_index = (
                today.month - offset
            )

            year_value = today.year

            while month_index <= 0:

                month_index += 12
                year_value -= 1

            total = (
                MedicalLicense.objects
                .filter(
                    application__in=applications,
                    issue_date__year=year_value,
                    issue_date__month=month_index,
                )
                .count()
            )

            license_monthly_data.append(
                total
            )

    recent_applications = (
        applications
        .select_related("applicant")
        .order_by("-created_at")[:8]
    )

    recent_activity = []

    for application in recent_applications:

        applicant_name = (
            application.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                application.applicant.username
            )

        recent_activity.append({
            "application_number":
                application.application_number
                or "Pending Number",

            "applicant_name":
                applicant_name,

            "profession":
                (
                    application.profession
                    .replace("_", " ")
                    .title()
                    if application.profession
                    else "Not Specified"
                ),

            "status":
                status_names.get(
                    application.status,
                    (
                        application.status
                        or "Unknown"
                    )
                    .replace("_", " ")
                    .title(),
                ),

            "created_at":
                application.created_at,
        })

    recent_renewals = (
        renewals
        .select_related(
            "applicant",
            "medical_license",
        )
        .order_by(
            "-submitted_at",
            "-created_at",
        )[:8]
    )

    renewal_activity = []

    for renewal in recent_renewals:

        applicant_name = (
            renewal.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                renewal.applicant.username
            )

        renewal_activity.append({
            "renewal_number":
                renewal.renewal_application_number
                or "Pending Number",

            "applicant_name":
                applicant_name,

            "license_number":
                (
                    renewal.medical_license
                    .license_number
                    if renewal.medical_license
                    else "Not Available"
                ),

            "status":
                renewal_status_names.get(
                    renewal.status,
                    (
                        renewal.status
                        or "Unknown"
                    )
                    .replace("_", " ")
                    .title(),
                ),

            "created_at":
                renewal.created_at,

            "submitted_at":
                renewal.submitted_at,
        })

    year_values = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
        .dates(
            "created_at",
            "year",
            order="DESC",
        )
    )

    profession_choices = (
        MedicalLicenseApplication.PROFESSION_CHOICES
        if hasattr(
            MedicalLicenseApplication,
            "PROFESSION_CHOICES",
        )
        else []
    )

    province_choices = (
        MedicalLicenseApplication.PROVINCE_CHOICES
        if hasattr(
            MedicalLicenseApplication,
            "PROVINCE_CHOICES",
        )
        else []
    )

    application_type_choices = (
        MedicalLicenseApplication
        .APPLICATION_TYPE_CHOICES
        if hasattr(
            MedicalLicenseApplication,
            "APPLICATION_TYPE_CHOICES",
        )
        else []
    )

    report_generated_at = timezone.now()

    context = {
        "total_applications":
            total_applications,

        "registered_workers":
            registered_workers,

        "active_licenses":
            active_licenses,

        "pending_applications":
            pending_applications,

        "licenses_issued":
            licenses_issued,

        "submitted_applications":
            submitted_applications,

        "under_review_applications":
            under_review_applications,

        "approved_applications":
            approved_applications,

        "rejected_applications":
            rejected_applications,

        "profession_data":
            profession_data,

        "province_data":
            province_data,

        "workplace_province_data":
            workplace_province_data,

        "status_data":
            status_data,

        "renewal_status_data":
            renewal_status_data,

        "monthly_data":
            monthly_data,

        "monthly_new_data":
            monthly_new_data,

        "monthly_renewal_data":
            monthly_renewal_data,

        "license_monthly_data":
            license_monthly_data,

        "qualification_data":
            qualification_data,

        "institution_data":
            institution_data,

        "graduate_data":
            graduate_data,

        "application_type_data":
            application_type_data,

        "recent_activity":
            recent_activity,

        "renewal_activity":
            renewal_activity,

        "total_renewals":
            total_renewals,

        "pending_renewals":
            pending_renewals,

        "under_review_renewals":
            under_review_renewals,

        "renewed_licenses":
            renewed_licenses,

        "rejected_renewals":
            rejected_renewals,

        "report_years":
            year_values,

        "selected_year":
            selected_year,

        "profession_choices":
            profession_choices,

        "selected_profession":
            selected_profession,

        "province_choices":
            province_choices,

        "selected_province":
            selected_province,

        "selected_workplace_province":
            selected_workplace_province,

        "application_type_choices":
            application_type_choices,

        "selected_application_type":
            selected_application_type,

        "report_generated_at":
            report_generated_at,
    }

    context.update(
        get_notification_context(
            request.user
        )
    )

    return render(
        request,
        "registrar/reports.html",
        context,
    )


@login_required
def export_reports_excel(request):

    if request.user.role != "registrar":
        return redirect("home")

    applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
        .select_related("applicant")
        .order_by("-created_at")
    )

    renewals = (
        LicenseRenewalApplication.objects
        .exclude(status="draft")
        .select_related(
            "applicant",
            "medical_license",
        )
        .order_by("-created_at")
    )

    year = request.GET.get(
        "year",
        "",
    ).strip()

    profession = request.GET.get(
        "profession",
        "",
    ).strip()

    province = request.GET.get(
        "province",
        "",
    ).strip()

    workplace_province = request.GET.get(
        "workplace_province",
        "",
    ).strip()

    application_type = request.GET.get(
        "application_type",
        "",
    ).strip()

    if year and year != "all":

        try:

            year_value = int(year)

            applications = applications.filter(
                created_at__year=year_value
            )

            renewals = renewals.filter(
                created_at__year=year_value
            )

        except ValueError:

            year = "all"

    if profession:

        applications = applications.filter(
            profession=profession
        )

    if province:

        applications = applications.filter(
            province=province
        )

    if workplace_province:

        applications = applications.filter(
            workplace_province=workplace_province
        )

    if application_type:

        applications = applications.filter(
            application_type=application_type
        )

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Registration Report"

    headers = [
        "Record Type",
        "Application Number",
        "Applicant Name",
        "Profession",
        "Specialization",
        "Province",
        "Workplace Province",
        "Qualification",
        "Institution",
        "Year Completed",
        "Application Type",
        "Status",
        "Submitted Date",
        "Reviewed Date",
        "License Number",
        "License Expiry",
    ]

    worksheet.append(headers)

    for application in applications:

        applicant_name = (
            application.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                application.applicant.username
            )

        license_number = ""

        license_expiry = ""

        license_record = getattr(
            application,
            "license",
            None,
        )

        if license_record:

            license_number = (
                license_record.license_number
            )

            if license_record.expiry_date:

                license_expiry = (
                    license_record
                    .expiry_date
                    .strftime("%Y-%m-%d")
                )

        worksheet.append([
            "New Registration",
            application.application_number or "",
            applicant_name,
            application.profession or "",
            application.specialization or "",
            application.province or "",
            application.workplace_province or "",
            application.qualification or "",
            application.institution or "",
            application.year_completed or "",
            application.application_type or "",
            application.get_status_display(),
            (
                application.submitted_at.strftime(
                    "%Y-%m-%d"
                )
                if application.submitted_at
                else ""
            ),
            (
                application.reviewed_at.strftime(
                    "%Y-%m-%d"
                )
                if application.reviewed_at
                else ""
            ),
            license_number,
            license_expiry,
        ])

    for renewal in renewals:

        applicant_name = (
            renewal.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                renewal.applicant.username
            )

        license_number = ""

        license_expiry = ""

        if renewal.medical_license:

            license_number = (
                renewal.medical_license
                .license_number
            )

            if renewal.medical_license.expiry_date:

                license_expiry = (
                    renewal.medical_license
                    .expiry_date
                    .strftime("%Y-%m-%d")
                )

        original_application = (
            renewal.medical_license.application
            if renewal.medical_license
            else None
        )

        profession_value = ""

        specialization_value = ""

        province_value = ""

        workplace_value = ""

        qualification_value = ""

        institution_value = ""

        year_completed_value = ""

        if original_application:

            profession_value = (
                original_application.profession
                or ""
            )

            specialization_value = (
                original_application.specialization
                or ""
            )

            province_value = (
                original_application.province
                or ""
            )

            workplace_value = (
                original_application
                .workplace_province
                or ""
            )

            qualification_value = (
                original_application
                .qualification
                or ""
            )

            institution_value = (
                original_application
                .institution
                or ""
            )

            year_completed_value = (
                original_application
                .year_completed
                or ""
            )

        worksheet.append([
            "License Renewal",
            renewal.renewal_application_number or "",
            applicant_name,
            profession_value,
            specialization_value,
            province_value,
            workplace_value,
            qualification_value,
            institution_value,
            year_completed_value,
            "Renewal",
            renewal.get_status_display(),
            (
                renewal.submitted_at.strftime(
                    "%Y-%m-%d"
                )
                if renewal.submitted_at
                else ""
            ),
            (
                renewal.reviewed_at.strftime(
                    "%Y-%m-%d"
                )
                if renewal.reviewed_at
                else ""
            ),
            license_number,
            license_expiry,
        ])

    for cell in worksheet[1]:

        font = copy(cell.font)
        font.bold = True
        cell.font = font

    column_widths = {
        "A": 20,
        "B": 24,
        "C": 28,
        "D": 22,
        "E": 24,
        "F": 18,
        "G": 22,
        "H": 25,
        "I": 30,
        "J": 16,
        "K": 18,
        "L": 18,
        "M": 18,
        "N": 18,
        "O": 24,
        "P": 18,
    }

    for column, width in column_widths.items():

        worksheet.column_dimensions[
            column
        ].width = width

    worksheet.freeze_panes = "A2"

    worksheet.auto_filter.ref = (
        worksheet.dimensions
    )

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

    response["Content-Disposition"] = (
        'attachment; filename="health_worker_registration_report.xlsx"'
    )

    return response


@login_required
def export_reports_pdf(request):

    if request.user.role != "registrar":
        return redirect("home")

    applications = (
        MedicalLicenseApplication.objects
        .exclude(status="draft")
        .select_related("applicant")
        .order_by("-created_at")
    )

    renewals = (
        LicenseRenewalApplication.objects
        .exclude(status="draft")
        .select_related(
            "applicant",
            "medical_license",
            "medical_license__application",
        )
        .order_by("-created_at")
    )

    year = request.GET.get(
        "year",
        "",
    ).strip()

    profession = request.GET.get(
        "profession",
        "",
    ).strip()

    province = request.GET.get(
        "province",
        "",
    ).strip()

    workplace_province = request.GET.get(
        "workplace_province",
        "",
    ).strip()

    application_type = request.GET.get(
        "application_type",
        "",
    ).strip()

    if year and year != "all":

        try:

            year_value = int(year)

            applications = applications.filter(
                created_at__year=year_value
            )

            renewals = renewals.filter(
                created_at__year=year_value
            )

        except ValueError:

            year = "all"

    if profession:

        applications = applications.filter(
            profession=profession
        )

    if province:

        applications = applications.filter(
            province=province
        )

    if workplace_province:

        applications = applications.filter(
            workplace_province=workplace_province
        )

    if application_type:

        applications = applications.filter(
            application_type=application_type
        )

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        textColor=HexColor("#102a43"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=HexColor("#6b7280"),
        spaceAfter=14,
    )

    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        textColor=HexColor("#344454"),
    )

    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9,
        textColor=HexColor("#ffffff"),
        fontName="Helvetica-Bold",
    )

    story = []

    story.append(
        Paragraph(
            "e-HealthWorkRegister",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "PNG Health Workers Online Registration System",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "Health Worker Registration and License Renewal Report",
            styles["Heading2"],
        )
    )

    story.append(
        Spacer(1, 8)
    )

    table_data = [
        [
            Paragraph(
                "Record",
                header_style,
            ),
            Paragraph(
                "Application",
                header_style,
            ),
            Paragraph(
                "Applicant",
                header_style,
            ),
            Paragraph(
                "Profession",
                header_style,
            ),
            Paragraph(
                "Status",
                header_style,
            ),
        ]
    ]

    for application in applications:

        applicant_name = (
            application.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                application.applicant.username
            )

        table_data.append([
            Paragraph(
                "New Registration",
                cell_style,
            ),
            Paragraph(
                str(
                    application.application_number
                    or ""
                ),
                cell_style,
            ),
            Paragraph(
                str(applicant_name),
                cell_style,
            ),
            Paragraph(
                str(
                    application.profession
                    or ""
                ),
                cell_style,
            ),
            Paragraph(
                str(
                    application.get_status_display()
                ),
                cell_style,
            ),
        ])

    for renewal in renewals:

        applicant_name = (
            renewal.applicant
            .get_full_name()
        )

        if not applicant_name:

            applicant_name = (
                renewal.applicant.username
            )

        profession_value = ""

        if renewal.medical_license:

            original_application = (
                renewal.medical_license.application
            )

            if original_application:

                profession_value = (
                    original_application.profession
                    or ""
                )

        table_data.append([
            Paragraph(
                "License Renewal",
                cell_style,
            ),
            Paragraph(
                str(
                    renewal
                    .renewal_application_number
                    or ""
                ),
                cell_style,
            ),
            Paragraph(
                str(applicant_name),
                cell_style,
            ),
            Paragraph(
                str(profession_value),
                cell_style,
            ),
            Paragraph(
                str(
                    renewal.get_status_display()
                ),
                cell_style,
            ),
        ])

    table = Table(
        table_data,
        colWidths=[
            30 * mm,
            36 * mm,
            45 * mm,
            38 * mm,
            28 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                HexColor("#102a43"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                HexColor("#ffffff"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                HexColor("#d9dee3"),
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    HexColor("#ffffff"),
                    HexColor("#f8fafc"),
                ],
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(table)

    document.build(story)

    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        'attachment; filename="health_worker_registration_report.pdf"'
    )

    return response