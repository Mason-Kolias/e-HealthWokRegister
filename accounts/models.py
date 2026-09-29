
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("health_worker", "Health Worker"),
        ("registrar", "Registrar"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="health_worker",
    )

    email = models.EmailField(unique=True)

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("application_submitted", "Application Submitted"),
        ("application_under_review", "Application Under Review"),
        ("application_approved", "Application Approved"),
        ("application_rejected", "Application Rejected"),
        ("application_resubmitted", "Application Resubmitted"),
        ("license_generated", "License Generated"),
        ("general", "General"),
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    notification_type = models.CharField(
        max_length=40,
        choices=NOTIFICATION_TYPES,
        default="general",
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # -----------------------------------------------------
    # ORIGINAL REGISTRATION APPLICATION
    # -----------------------------------------------------

    related_application = models.ForeignKey(
        "health_workers.MedicalLicenseApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    # -----------------------------------------------------
    # LICENSE RENEWAL APPLICATION
    # -----------------------------------------------------

    related_renewal = models.ForeignKey(
        "health_workers.LicenseRenewalApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"
