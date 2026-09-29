from django.contrib import admin
from django.urls import path, include

from accounts import views as account_views


urlpatterns = [

    # Landing page
    path(
        "",
        account_views.landing_page,
        name="home"
    ),

    # Django admin
    path(
        "admin/",
        admin.site.urls
    ),

    # Login
    path(
        "login/",
        account_views.login_view,
        name="login"
    ),

    # Logout
    path(
        "logout/",
        account_views.logout_view,
        name="logout"
    ),

    # Health Worker URLs
    path(
        "",
        include("health_workers.urls")
    ),

    # Registrar URLs
    path(
        "registrar/",
        include("registrar.urls")
    ),
]