from django.urls import path

from . import renewal_views
from . import views


urlpatterns = [
    path(
        "health-worker/dashboard/",
        views.health_worker_dashboard,
        name="health_worker_dashboard",
    ),

    path(
        "health-worker/apply/",
        views.medical_license_application,
        name="medical_license_application",
    ),

    path(
        "health-worker/application/<int:application_id>/review/",
        views.review_application,
        name="review_application",
    ),

    path(
        "health-worker/application/<int:application_id>/submit/",
        views.submit_application,
        name="submit_application",
    ),

    path(
        "health-worker/license-renewal/",
        renewal_views.license_renewal_application,
        name="license_renewal_application",
    ),

    path(
        "health-worker/license-renewal/<int:renewal_id>/review/",
        renewal_views.review_renewal_application,
        name="review_renewal_application",
    ),

    path(
        "health-worker/license-renewal/<int:renewal_id>/submit/",
        renewal_views.submit_renewal_application,
        name="submit_renewal_application",
    ),

    path(
        "health-worker/license-renewal/<int:renewal_id>/download/",
        renewal_views.download_renewed_license,
        name="download_renewed_license",
    ),
]