
from django.urls import path

from . import health_worker_records_views
from . import renewal_views
from . import views


urlpatterns = [

    # =====================================================
    # REGISTRAR DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        views.registrar_dashboard,
        name="registrar_dashboard",
    ),


    # =====================================================
    # NEW HEALTH WORKER APPLICATIONS
    # =====================================================

    path(
        "applications/",
        views.registrar_review_applications,
        name="registrar_review_applications",
    ),

    path(
        "application/<int:application_id>/review/",
        views.registrar_review_application,
        name="registrar_review_application",
    ),


    # =====================================================
    # HEALTH WORKER RECORDS
    # =====================================================

    path(
        "health-workers/",
        health_worker_records_views.health_worker_records,
        name="registrar_health_worker_records",
    ),

    path(
        "health-worker/<int:application_id>/",
        health_worker_records_views.health_worker_record_detail,
        name="registrar_health_worker_record_detail",
    ),


    # =====================================================
    # GENERATE NEW MEDICAL LICENSE
    # =====================================================

    path(
        "generate-license/",
        views.generate_license_page,
        name="generate_license_page",
    ),

    path(
        "generate-license/<int:application_id>/",
        views.generate_medical_license,
        name="generate_medical_license",
    ),

    path(
        "download-license/<int:application_id>/",
        views.download_medical_license,
        name="download_medical_license",
    ),


    # =====================================================
    # LICENSE RENEWAL APPLICATIONS
    # =====================================================

    path(
        "renewals/",
        renewal_views.registrar_renewal_applications,
        name="registrar_renewal_applications",
    ),

    path(
        "renewal/<int:renewal_id>/review/",
        renewal_views.registrar_review_renewal,
        name="registrar_review_renewal",
    ),

    path(
        "renewal/<int:renewal_id>/approve/",
        renewal_views.approve_renewal,
        name="approve_renewal",
    ),

    path(
        "renewal/<int:renewal_id>/reject/",
        renewal_views.reject_renewal,
        name="reject_renewal",
    ),


    # =====================================================
    # GENERATE RENEWED MEDICAL LICENSE
    # =====================================================

    path(
        "renewed-licenses/",
        renewal_views.generate_renewed_licenses,
        name="generate_renewed_licenses",
    ),

    path(
        "renewed-licenses/<int:renewal_id>/generate/",
        renewal_views.generate_renewed_license,
        name="generate_renewed_license",
    ),


    # =====================================================
    # REPORTS
    # =====================================================

    path(
        "reports/",
        views.registrar_reports,
        name="registrar_reports",
    ),

    path(
        "reports/excel/",
        views.export_reports_excel,
        name="export_reports_excel",
    ),

    path(
        "reports/pdf/",
        views.export_reports_pdf,
        name="export_reports_pdf",
    ),
]

