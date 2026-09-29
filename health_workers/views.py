import base64
import binascii

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from accounts.models import Notification

from .forms import (
    DOCUMENT_TYPES,
    ApplicationDocumentFormSet,
    MedicalLicenseApplicationForm,
)
from .models import MedicalLicenseApplication


User = get_user_model()


WIZARD_SECTIONS = {
    1: [
        "full_name",
        "date_of_birth",
        "gender",
        "nationality",
    ],
    2: [
        "phone_number",
        "email",
        "residential_address",
        "province",
        "district",
    ],
    3: [
        "profession",
        "professional_registration_number",
        "specialization",
        "years_of_experience",
    ],
    4: [
        "qualification",
        "institution",
        "campus",
        "institution_province",
        "country_of_qualification",
        "year_started",
        "year_completed",
        "graduation_status",
    ],
    5: [
        "current_employer",
        "position",
        "workplace_province",
        "employment_start_date",
    ],
}


REQUIRED_APPLICATION_FIELDS = [
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
    "qualification",
    "institution",
    "country_of_qualification",
    "year_completed",
    "graduation_status",
]


LOCKED_APPLICATION_STATUSES = [
    "submitted",
    "under_review",
    "approved",
    "license_generated",
]


def notify_registrars(
    application,
    title,
    message,
    notification_type,
):
    registrars = User.objects.filter(
        role="registrar",
        is_active=True,
    )

    notifications = [
        Notification(
            recipient=registrar,
            title=title,
            message=message,
            notification_type=notification_type,
            related_application=application,
        )
        for registrar in registrars
    ]

    if notifications:
        Notification.objects.bulk_create(notifications)


def create_health_worker_notification(
    application,
    title,
    message,
    notification_type,
):
    Notification.objects.create(
        recipient=application.applicant,
        title=title,
        message=message,
        notification_type=notification_type,
        related_application=application,
    )


def save_signature(
    application,
    signature_data,
):
    if not signature_data:
        return False

    prefix = "data:image/png;base64,"

    if not signature_data.startswith(prefix):
        return False

    try:
        encoded = signature_data.split(",", 1)[1]

        decoded = base64.b64decode(
            encoded,
            validate=True,
        )

        filename = (
            f"{application.application_number}_signature.png"
        )

        application.signature.save(
            filename,
            ContentFile(decoded),
            save=False,
        )

        application.save(
            update_fields=[
                "signature",
                "updated_at",
            ]
        )

        return True

    except (
        ValueError,
        TypeError,
        binascii.Error,
    ):
        return False


def get_required_document_types():
    return {
        document_type
        for document_type, label in DOCUMENT_TYPES
    }


def document_file_exists(document):
    if not document:
        return False

    if not document.document_file:
        return False

    try:
        return document.document_file.storage.exists(
            document.document_file.name
        )
    except Exception:
        return False


def get_uploaded_document_types(application):
    if application is None:
        return set()

    uploaded_types = set()

    for document in application.documents.all():
        if document_file_exists(document):
            uploaded_types.add(
                document.document_type
            )

    return uploaded_types


def get_missing_documents(application):
    required = get_required_document_types()
    uploaded = get_uploaded_document_types(application)

    return required - uploaded


def get_application_completion_errors(application):
    errors = []

    for field_name in REQUIRED_APPLICATION_FIELDS:
        value = getattr(
            application,
            field_name,
            None,
        )

        if value in [None, ""]:
            field = MedicalLicenseApplicationForm.base_fields.get(
                field_name
            )

            if field:
                label = field.label
            else:
                label = field_name.replace(
                    "_",
                    " ",
                ).title()

            errors.append(
                f"{label} is required."
            )

    missing_documents = get_missing_documents(
        application
    )

    if missing_documents:
        document_labels = dict(DOCUMENT_TYPES)

        for document_type in sorted(
            missing_documents
        ):
            label = document_labels.get(
                document_type,
                document_type.replace(
                    "_",
                    " ",
                ).title(),
            )

            errors.append(
                f"{label} has not been uploaded."
            )

    return errors


def make_application_form_readonly(form):
    for field in form.fields.values():
        field.disabled = True
        field.required = False
        field.widget.attrs["disabled"] = "disabled"

    return form


def make_document_formset_readonly(
    document_formset,
):
    for document_form in document_formset.forms:
        for field in document_form.fields.values():
            field.disabled = True
            field.required = False
            field.widget.attrs["disabled"] = "disabled"

    return document_formset


@login_required
@ensure_csrf_cookie
def medical_license_application(request):

    if request.user.role != "health_worker":
        messages.error(
            request,
            "Only health workers can access the medical license application.",
        )
        return redirect("home")

    application = (
        MedicalLicenseApplication.objects
        .filter(
            applicant=request.user,
        )
        .prefetch_related("documents")
        .first()
    )

    if (
        application is None
        and request.method == "GET"
    ):
        application = (
            MedicalLicenseApplication.objects.create(
                applicant=request.user,
                application_type="new",
                status="draft",
            )
        )

    is_locked = (
        application is not None
        and application.status
        in LOCKED_APPLICATION_STATUSES
    )

    is_rejected = (
        application is not None
        and application.status == "rejected"
    )

    try:
        initial_step = int(
            request.GET.get(
                "step",
                "1",
            )
        )
    except (
        TypeError,
        ValueError,
    ):
        initial_step = 1

    initial_step = max(
        1,
        min(7, initial_step),
    )

    if (
        is_locked
        and request.method == "POST"
    ):
        messages.info(
            request,
            "Your application has already been submitted and cannot be edited or submitted again unless it is rejected.",
        )
        return redirect(
            "medical_license_application"
        )

    form = MedicalLicenseApplicationForm(
        instance=application
    )

    document_formset = ApplicationDocumentFormSet(
        prefix="documents",
        application=application,
    )

    if (
        request.method == "POST"
        and not is_locked
    ):

        try:
            current_step = int(
                request.POST.get(
                    "current_step",
                    "1",
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            current_step = 1

        current_step = max(
            1,
            min(7, current_step),
        )

        if current_step <= 5:

            if application is None:
                application = (
                    MedicalLicenseApplication(
                        applicant=request.user,
                        application_type="new",
                        status="draft",
                    )
                )

            form = MedicalLicenseApplicationForm(
                request.POST,
                instance=application,
            )

            section_fields = WIZARD_SECTIONS[
                current_step
            ]

            for field_name in form.fields:
                if field_name not in section_fields:
                    form.fields[field_name].required = False
                else:
                    form.fields[field_name].required = (
            field_name in REQUIRED_APPLICATION_FIELDS
        )
                

            if form.is_valid():

                application = form.save(
                    commit=False
                )

                application.applicant = (
                    request.user
                )

                application.application_type = (
                    "new"
                )

                if application.status not in [
                    "draft",
                    "rejected",
                ]:
                    application.status = "draft"

                application.save()

                return redirect(
                    f"/health-worker/apply/?step={current_step + 1}"
                )

            initial_step = current_step

            document_formset = (
                ApplicationDocumentFormSet(
                    prefix="documents",
                    application=application,
                )
            )

        elif current_step == 6:

            if application is None:
                messages.error(
                    request,
                    "Please complete the previous application sections first.",
                )
                return redirect(
                    "/health-worker/apply/?step=1"
                )

            document_formset = (
                ApplicationDocumentFormSet(
                    request.POST,
                    request.FILES,
                    prefix="documents",
                    application=application,
                )
            )

            if document_formset.is_valid():

                document_formset.save()

                messages.success(
                    request,
                    "Your supporting documents have been saved. Please review your application before submitting.",
                )

                return redirect(
                    "/health-worker/apply/?step=7"
                )

            initial_step = 6

        elif current_step == 7:

            if application is None:
                messages.error(
                    request,
                    "Please complete your application before continuing.",
                )
                return redirect(
                    "/health-worker/apply/?step=1"
                )

            completion_errors = (
                get_application_completion_errors(
                    application
                )
            )

            if completion_errors:
                messages.error(
                    request,
                    "Please complete all required application information and supporting documents before submitting.",
                )
                return redirect(
                    "/health-worker/apply/?step=7"
                )

            if not request.POST.get(
                "declaration"
            ):
                messages.error(
                    request,
                    "Please confirm the declaration before submitting.",
                )
                return redirect(
                    "/health-worker/apply/?step=7"
                )

            signature_data = request.POST.get(
                "signature_data"
            )

            if (
                not signature_data
                and not application.signature
            ):
                messages.error(
                    request,
                    "Please provide your signature before submitting.",
                )
                return redirect(
                    "/health-worker/apply/?step=7"
                )

            if application.status not in [
                "draft",
                "rejected",
            ]:
                messages.info(
                    request,
                    "This application has already been submitted and cannot be submitted again unless it is rejected.",
                )
                return redirect(
                    "medical_license_application"
                )

            was_rejected = (
                application.status == "rejected"
            )

            if signature_data:
                if not save_signature(
                    application,
                    signature_data,
                ):
                    messages.error(
                        request,
                        "The signature could not be saved. Please sign again.",
                    )
                    return redirect(
                        "/health-worker/apply/?step=7"
                    )

            application.status = "submitted"
            application.application_type = "new"
            application.submitted_at = (
                timezone.now()
            )
            application.rejection_reason = ""

            application.save(
                update_fields=[
                    "status",
                    "application_type",
                    "submitted_at",
                    "rejection_reason",
                    "updated_at",
                ]
            )

            if was_rejected:

                registrar_title = (
                    "Health Worker Application Resubmitted"
                )

                notification_type = (
                    "application_resubmitted"
                )

                worker_title = (
                    "Application Resubmitted"
                )

                worker_message = (
                    f"Your medical license application "
                    f"{application.application_number} "
                    "has been resubmitted successfully for review."
                )

                success_message = (
                    "Your medical license application has been resubmitted successfully."
                )

            else:

                registrar_title = (
                    "New Health Worker Application"
                )

                notification_type = (
                    "application_submitted"
                )

                worker_title = (
                    "Application Submitted"
                )

                worker_message = (
                    f"Your medical license application "
                    f"{application.application_number} "
                    "has been successfully submitted for review."
                )

                success_message = (
                    "Your medical license application has been submitted successfully."
                )

            notify_registrars(
                application,
                registrar_title,
                (
                    f"{application.full_name or application.applicant.email} "
                    f"has submitted application "
                    f"{application.application_number} "
                    "for review."
                ),
                notification_type,
            )

            create_health_worker_notification(
                application,
                worker_title,
                worker_message,
                notification_type,
            )

            messages.success(
                request,
                success_message,
            )

            return redirect(
                "health_worker_dashboard"
            )

    if is_locked:
        form = make_application_form_readonly(
            form
        )

        document_formset = (
            make_document_formset_readonly(
                document_formset
            )
        )

    if (
        is_rejected
        and application.rejection_reason
    ):
        messages.warning(
            request,
            "Your previous application was rejected. Please review the Registrar's reason, correct the application, and resubmit it.",
        )

    return render(
        request,
        "health_workers/application_for_medical_license.html",
        {
            "form": form,
            "application_form": form,
            "document_formset": document_formset,
            "application": application,
            "initial_step": initial_step,
            "document_types": DOCUMENT_TYPES,
            "is_locked": is_locked,
            "is_rejected": is_rejected,
        },
    )


@login_required
def review_application(
    request,
    application_id,
):
    if request.user.role != "health_worker":
        return redirect("home")

    application = get_object_or_404(
        MedicalLicenseApplication,
        id=application_id,
        applicant=request.user,
    )

    return redirect(
        f"/health-worker/apply/?step=7"
    )


@login_required
@require_POST
def submit_application(
    request,
    application_id,
):
    if request.user.role != "health_worker":
        return redirect("home")

    application = get_object_or_404(
        MedicalLicenseApplication,
        id=application_id,
        applicant=request.user,
    )

    if application.status not in [
        "draft",
        "rejected",
    ]:
        messages.info(
            request,
            "This application has already been submitted and cannot be submitted again unless it is rejected.",
        )
        return redirect(
            "medical_license_application"
        )

    completion_errors = (
        get_application_completion_errors(
            application
        )
    )

    if completion_errors:
        messages.error(
            request,
            "Please complete all required information and documents.",
        )
        return redirect(
            "/health-worker/apply/?step=7"
        )

    if not request.POST.get(
        "declaration"
    ):
        messages.error(
            request,
            "Please confirm the declaration before submitting.",
        )
        return redirect(
            "/health-worker/apply/?step=7"
        )

    signature_data = request.POST.get(
        "signature_data"
    )

    if signature_data:

        if not save_signature(
            application,
            signature_data,
        ):
            messages.error(
                request,
                "The signature could not be saved. Please sign again.",
            )
            return redirect(
                "/health-worker/apply/?step=7"
            )

    elif not application.signature:

        messages.error(
            request,
            "Please provide your signature before submitting.",
        )
        return redirect(
            "/health-worker/apply/?step=7"
        )

    was_rejected = (
        application.status == "rejected"
    )

    application.status = "submitted"
    application.submitted_at = timezone.now()
    application.rejection_reason = ""

    application.save(
        update_fields=[
            "status",
            "submitted_at",
            "rejection_reason",
            "updated_at",
        ]
    )

    notification_type = (
        "application_resubmitted"
        if was_rejected
        else "application_submitted"
    )

    title = (
        "Application Resubmitted"
        if was_rejected
        else "Application Submitted"
    )

    message = (
        f"Your medical license application "
        f"{application.application_number} "
        f"has been "
        f"{'resubmitted' if was_rejected else 'submitted'} "
        "successfully for review."
    )

    notify_registrars(
        application,
        (
            "Health Worker Application Resubmitted"
            if was_rejected
            else "New Health Worker Application"
        ),
        (
            f"{application.full_name or application.applicant.email} "
            f"has submitted application "
            f"{application.application_number} "
            "for review."
        ),
        notification_type,
    )

    create_health_worker_notification(
        application,
        title,
        message,
        notification_type,
    )

    messages.success(
        request,
        message,
    )

    return redirect(
        "health_worker_dashboard"
    )


@login_required
def health_worker_dashboard(request):

    if request.user.role != "health_worker":
        return redirect("home")

    application = (
        MedicalLicenseApplication.objects
        .filter(
            applicant=request.user,
        )
        .select_related("license")
        .prefetch_related("documents")
        .order_by("-created_at")
        .first()
    )

    application_status = "No Application"
    application_status_class = "no-application"

    document_count = 0
    application_progress = 0

    license_status = "Not Available"
    license_available = False
    license = None

    if application:

        document_count = len(
            get_uploaded_document_types(
                application
            )
        )

        status_labels = {
            "draft": "Draft",
            "submitted": "Application Submitted",
            "under_review": "Under Review",
            "approved": "Approved",
            "rejected": "Action Required",
            "license_generated": "License Generated",
        }

        status_classes = {
            "draft": "draft",
            "submitted": "submitted",
            "under_review": "under-review",
            "approved": "approved",
            "rejected": "rejected",
            "license_generated": "license-generated",
        }

        application_status = status_labels.get(
            application.status,
            "Unknown",
        )

        application_status_class = status_classes.get(
            application.status,
            "no-application",
        )

        if application.status == "draft":

            completed_fields = 0
            total_fields = 0

            for section_fields in (
                WIZARD_SECTIONS.values()
            ):

                for field_name in section_fields:

                    total_fields += 1

                    value = getattr(
                        application,
                        field_name,
                        None,
                    )

                    if value not in [
                        None,
                        "",
                    ]:
                        completed_fields += 1

            if total_fields:

                field_progress = int(
                    completed_fields
                    / total_fields
                    * 70
                )

            else:
                field_progress = 0

            document_progress = int(
                document_count
                / len(DOCUMENT_TYPES)
                * 30
            )

            application_progress = min(
                100,
                field_progress
                + document_progress,
            )

        elif application.status == "submitted":
            application_progress = 60

        elif application.status == "under_review":
            application_progress = 75

        elif application.status == "approved":
            application_progress = 90

        elif application.status == "license_generated":
            application_progress = 100

        elif application.status == "rejected":
            application_progress = 0

        license = getattr(
            application,
            "license",
            None,
        )

        if (
            application.status
            == "license_generated"
            and license
        ):

            license_available = True
            license_status = (
                "License Available"
            )

        elif application.status == "approved":

            license_status = (
                "Approved - License Processing"
            )

        elif application.status == "under_review":

            license_status = "Under Review"

        elif application.status == "submitted":

            license_status = "Pending Review"

        elif application.status == "rejected":

            license_status = "Action Required"

        else:

            license_status = "License Pending"

    notifications = (
        Notification.objects
        .filter(
            recipient=request.user,
        )
        .order_by("-created_at")[:10]
    )

    unread_notifications = (
        Notification.objects
        .filter(
            recipient=request.user,
            is_read=False,
        )
        .count()
    )

    return render(
        request,
        "health_workers/health_worker_dashboard.html",
        {
            "application": application,
            "application_status": application_status,
            "application_status_class": application_status_class,
            "document_count": document_count,
            "application_progress": application_progress,
            "license_status": license_status,
            "license_available": license_available,
            "license": license,
            "notifications": notifications,
            "unread_notifications": unread_notifications,
        },
    )
    
    
    