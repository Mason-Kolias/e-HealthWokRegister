from django.conf import settings
from django.db import models
from django.utils import timezone


class MedicalLicenseApplication(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("license_generated", "License Generated"),
    ]

    APPLICATION_TYPE_CHOICES = [
        ("new", "New Registration"),
        ("renewal", "License Renewal"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    GRADUATION_STATUS_CHOICES = [
        ("graduated", "Graduated"),
        ("final_year", "Final Year Student"),
        ("completed", "Course Completed"),
    ]

    PROFESSION_CHOICES = [
         ("medical_officer", "Medical Graduate"),
    ("nursing", "Nursing Graduate"),
    ("midwifery", "Midwifery Graduate"),
    ("health_extension", "Health Extension Officer Graduate"),
    ("community_health", "Community Health Worker Graduate"),
    ("pharmacy", "Pharmacy Graduate"),
    ("medical_laboratory", "Medical Laboratory Science Graduate"),
    ("physiotherapy", "Physiotherapy Graduate"),
    ("radiography", "Radiography Graduate"),
    ("dentistry", "Dentistry Graduate"),
     
    ]

    PROVINCE_CHOICES = [
        ("Central", "Central"),
        ("Gulf", "Gulf"),
        ("Milne Bay", "Milne Bay"),
        ("NCD", "National Capital District"),
        ("Western", "Western"),
        ("Eastern Highlands", "Eastern Highlands"),
        ("Southern Highlands", "Southern Highlands"),
        ("Western Highlands", "Western Highlands"),
        ("Jiwaka", "Jiwaka"),
        ("Simbu", "Simbu"),
        ("Hela", "Hela"),
        ("Enga", "Enga"),
        ("East New Britain", "East New Britain"),
        ("West New Britain", "West New Britain"),
        ("New Ireland", "New Ireland"),
        ("Manus", "Manus"),
        ("Bougainville", "Bougainville"),
        ("Northern", "Northern"),
        ("Morobe", "Morobe"),
        ("Madang", "Madang"),
    ]

    INSTITUTION_CHOICES = [
        ("UPNG", "University of Papua New Guinea (UPNG)"),
        ("PAU", "Pacific Adventist University (PAU)"),
        ("DWU", "Divine Word University (DWU)"),
        ("WPU", "Western Pacific University (WPU)"),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="license_applications"
    )

    application_type = models.CharField(
        max_length=20,
        choices=APPLICATION_TYPE_CHOICES,
        default="new"
    )

    application_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    nationality = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    residential_address = models.TextField(
        blank=True,
        null=True
    )

    province = models.CharField(
        max_length=100,
        choices=PROVINCE_CHOICES,
        blank=True,
        null=True
    )

    district = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    profession = models.CharField(
        max_length=100,
        choices=PROFESSION_CHOICES,
        blank=True,
        null=True
    )

    professional_registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    specialization = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    qualification = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    institution = models.CharField(
        max_length=20,
        choices=INSTITUTION_CHOICES,
        blank=True,
        null=True
    )

    campus = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    institution_province = models.CharField(
        max_length=100,
        choices=PROVINCE_CHOICES,
        blank=True,
        null=True
    )

    country_of_qualification = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    year_started = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    year_completed = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    graduation_status = models.CharField(
        max_length=30,
        choices=GRADUATION_STATUS_CHOICES,
        blank=True,
        null=True
    )

    current_employer = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    position = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    workplace_province = models.CharField(
        max_length=100,
        choices=PROVINCE_CHOICES,
        blank=True,
        null=True
    )

    employment_start_date = models.DateField(
        blank=True,
        null=True
    )

    signature = models.FileField(
        upload_to="health_worker_signatures/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="draft"
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_license_applications"
    )

    rejection_reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["applicant"],
                name="one_application_per_health_worker"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.application_number:
            year = timezone.now().year

            last_application = (
                MedicalLicenseApplication.objects
                .filter(
                    application_number__startswith=f"PNG-HW-{year}-"
                )
                .order_by("-id")
                .first()
            )

            if last_application:
                last_number = int(
                    last_application.application_number.split("-")[-1]
                )
                next_number = last_number + 1
            else:
                next_number = 1

            self.application_number = (
                f"PNG-HW-{year}-{next_number:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.application_number} - "
            f"{self.full_name or 'Incomplete Application'}"
        )


class ApplicationDocument(models.Model):

    DOCUMENT_TYPES = [
        ("current_transcript", "Current Transcript"),
        ("current_school_id", "Current School ID"),
        ("school_confirmation", "School Confirmation Letter"),
        ("id_photo", "ID Sized Photo"),
        ("grade12_certificate", "National Grade 12 Certificate"),
        ("registration_fee_receipt", "Receipt for Registration Fee"),
    ]

    application = models.ForeignKey(
        MedicalLicenseApplication,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    document_file = models.FileField(
        upload_to="health_worker_documents/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["application", "document_type"],
                name="unique_document_type_per_application"
            )
        ]

    def __str__(self):
        return (
            f"{self.application.application_number} - "
            f"{self.get_document_type_display()}"
        )


class MedicalLicense(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("revoked", "Revoked"),
    ]

    application = models.OneToOneField(
        MedicalLicenseApplication,
        on_delete=models.CASCADE,
        related_name="license"
    )

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_licenses"
    )

    license_number = models.CharField(
        max_length=50,
        unique=True
    )

    issue_date = models.DateField()

    expiry_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    license_document = models.FileField(
        upload_to="medical_licenses/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.license_number} - {self.applicant}"


class LicenseRenewalApplication(models.Model):

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("renewed", "Renewed"),
    ]

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="license_renewal_applications"
    )

    medical_license = models.ForeignKey(
        MedicalLicense,
        on_delete=models.CASCADE,
        related_name="renewal_applications"
    )

    renewal_application_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    current_employer = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    current_work_location = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    payment_receipt = models.FileField(
        upload_to="renewal_receipts/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    rejection_reason = models.TextField(
        blank=True
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_renewals"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if not self.renewal_application_number:
            year = timezone.now().year

            last_renewal = (
                LicenseRenewalApplication.objects
                .filter(
                    renewal_application_number__startswith=f"PNG-REN-{year}-"
                )
                .order_by("-id")
                .first()
            )

            if last_renewal:
                last_number = int(
                    last_renewal.renewal_application_number.split("-")[-1]
                )
                next_number = last_number + 1
            else:
                next_number = 1

            self.renewal_application_number = (
                f"PNG-REN-{year}-{next_number:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.renewal_application_number} - "
            f"{self.applicant}"
        )