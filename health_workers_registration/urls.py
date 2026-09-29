from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts import views as account_views


urlpatterns = [
    path("", account_views.landing_page, name="home"),

    path("admin/", admin.site.urls),

    path(
        "login/",
        account_views.login_view,
        name="login",
    ),

    path(
        "logout/",
        account_views.logout_view,
        name="logout",
    ),

    path(
        "profile/",
        account_views.profile,
        name="profile",
    ),

    path(
        "profile/edit/",
        account_views.edit_profile,
        name="edit_profile",
    ),

    path(
        "profile/change-password/",
        account_views.change_password,
        name="change_password",
    ),

    path(
        "notifications/",
        account_views.notifications,
        name="notifications",
    ),

    path(
        "notifications/<int:notification_id>/read/",
        account_views.mark_notification_read,
        name="mark_notification_read",
    ),

    path(
        "notifications/mark-all-read/",
        account_views.mark_all_notifications_read,
        name="mark_all_notifications_read",
    ),

    path(
        "",
        include("health_workers.urls"),
    ),

    path(
        "registrar/",
        include("registrar.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )