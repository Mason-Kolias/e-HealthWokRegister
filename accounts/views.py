from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import ProfileUpdateForm
from .models import Notification


@ensure_csrf_cookie
def landing_page(request):
    return render(
        request,
        "home.html",
        {
            "show_login": False,
        },
    )


@ensure_csrf_cookie
def login_view(request):
    if request.method != "POST":
        return redirect("home")

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")
    role = request.POST.get("role", "")

    error = None

    if not username:
        error = "Please enter your email address."

    elif not password:
        error = "Please enter your password."

    elif not role:
        error = "Please select a role."

    else:
        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            error = "Incorrect email or password."

        elif user.role != role:
            error = "The selected role does not match your account."

        else:
            login(request, user)

            if user.role == "registrar":
                return redirect("registrar_dashboard")

            if user.role == "health_worker":
                return redirect("health_worker_dashboard")

            logout(request)
            error = "Your account does not have a valid role."

    return render(
        request,
        "home.html",
        {
            "login_error": error,
            "login_username": username,
            "login_role": role,
            "show_login": True,
        },
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.user.role == "registrar":
        return redirect("registrar_dashboard")

    if request.user.role == "health_worker":
        return redirect("health_worker_dashboard")

    logout(request)
    return redirect("home")



@login_required
def profile(request):
    if request.user.role == "registrar":
        return render(
            request,
            "accounts/registrar_profile.html",
        )

    return render(
        request,
        "accounts/profile.html",
    )


@login_required
def edit_profile(request):
    user = request.user

    if user.role == "registrar":
        base_template = "registrar/registrar_base.html"
    else:
        base_template = "health_workers/health_worker_base.html"

    if request.method == "POST":
        old_photo_name = ""

        if user.profile_photo:
            old_photo_name = user.profile_photo.name

        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            user_instance=user,
        )

        if form.is_valid():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]

            new_photo = form.cleaned_data.get("profile_photo")
            remove_photo = form.cleaned_data.get(
                "remove_profile_photo"
            )

            if remove_photo:
                if user.profile_photo:
                    user.profile_photo.delete(save=False)

                user.profile_photo = ""

            elif new_photo:
                if user.profile_photo:
                    user.profile_photo.delete(save=False)

                user.profile_photo = new_photo

            user.save()

            if (
                old_photo_name
                and not user.profile_photo
            ):
                default_storage.delete(old_photo_name)

            messages.success(
                request,
                "Your profile has been updated successfully.",
            )

            return redirect("profile")

    else:
        form = ProfileUpdateForm(
            user_instance=user,
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form": form,
            "user": user,
            "base_template": base_template,
        },
    
    )
  


@login_required
def change_password(request):
    if request.user.role == "registrar":
        base_template = "registrar/registrar_base.html"
    else:
        base_template = "health_workers/health_worker_base.html"

    if request.method == "POST":
        form = PasswordChangeForm(
            request.user,
            request.POST,
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            return redirect("profile")

    else:
        form = PasswordChangeForm(
            request.user,
        )

    return render(
        request,
        "accounts/change_password.html",
        {
            "form": form,
            "user": request.user,
            "base_template": base_template,
        },
    )

"""   
@login_required
def notifications(request):
    if request.user.role == "registrar":
        base_template = "registrar/registrar_base.html"
    else:
        base_template = "health_workers/health_worker_base.html"

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_count = user_notifications.filter(
        is_read=False
    ).count()

    return render(
        request,
        "accounts/notifications.html",
        {
            "user": request.user,
            "base_template": base_template,
            "notifications": user_notifications,
            "unread_count": unread_count,
        },
    )
"""

@login_required
def notifications(request):

    user_notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_count = user_notifications.filter(
        is_read=False
    ).count()

    context = {
        "user": request.user,
        "notifications": user_notifications,
        "unread_count": unread_count,
    }

    if request.user.role == "registrar":

        return render(
            request,
            "accounts/registrar_notifications.html",
            context,
        )

    return render(
        request,
      "accounts/health_worker_notifications.html",
        context,
    )
    
    

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user,
    )

    notification.is_read = True
    notification.save(
        update_fields=["is_read"]
    )

    # =====================================================
    # RENEWAL NOTIFICATION
    # =====================================================

    if notification.related_renewal:
        renewal = notification.related_renewal

        if request.user.role == "registrar":
            return redirect(
                "registrar_review_renewal",
                renewal_id=renewal.id,
            )

        if request.user.role == "health_worker":
            if renewal.status == "draft":
                return redirect(
                    "review_renewal_application",
                    renewal_id=renewal.id,
                )

            return redirect(
                "license_renewal_application"
            )

    # =====================================================
    # ORIGINAL APPLICATION NOTIFICATION
    # =====================================================

    if notification.related_application:
        application = notification.related_application

        if request.user.role == "registrar":
            return redirect(
                "registrar_review_application",
                application_id=application.id,
            )

        if request.user.role == "health_worker":
            if application.status == "draft":
                return redirect(
                    "review_application",
                    application_id=application.id,
                )

            return redirect(
                "health_worker_dashboard"
            )

    return redirect("notifications")


@login_required
def mark_all_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(
            recipient=request.user,
            is_read=False,
        ).update(
            is_read=True
        )

    return redirect("notifications")