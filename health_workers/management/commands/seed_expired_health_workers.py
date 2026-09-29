
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from health_workers.models import (
    MedicalLicense,
    MedicalLicenseApplication,
)


User = get_user_model()


HEALTH_WORKERS = [
    {
        "first_name": "Michael",
        "last_name": "Kila",
        "profession": "doctor",
        "province": "NCD",
        "qualification": "Bachelor of Medicine and Bachelor of Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Grace",
        "last_name": "Wama",
        "profession": "registered_nurse",
        "province": "Western Highlands",
        "qualification": "Bachelor of Nursing",
        "institution": "PAU",
        "campus": "Koiari Park Campus",
    },
    {
        "first_name": "Peter",
        "last_name": "Arua",
        "profession": "community_health_worker",
        "province": "Morobe",
        "qualification": "Diploma in Community Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Anna",
        "last_name": "Moke",
        "profession": "midwife",
        "province": "Madang",
        "qualification": "Bachelor of Midwifery",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "David",
        "last_name": "Kora",
        "profession": "pharmacist",
        "province": "Eastern Highlands",
        "qualification": "Bachelor of Pharmacy",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Lucy",
        "last_name": "Tamo",
        "profession": "medical_laboratory",
        "province": "East New Britain",
        "qualification": "Bachelor of Medical Laboratory Science",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Samuel",
        "last_name": "Naru",
        "profession": "health_extension_officer",
        "province": "Simbu",
        "qualification": "Bachelor of Rural Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Rebecca",
        "last_name": "Maro",
        "profession": "registered_nurse",
        "province": "Central",
        "qualification": "Bachelor of Nursing",
        "institution": "PAU",
        "campus": "Koiari Park Campus",
    },
    {
        "first_name": "John",
        "last_name": "Pala",
        "profession": "doctor",
        "province": "Milne Bay",
        "qualification": "Bachelor of Medicine and Bachelor of Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Janet",
        "last_name": "Kewa",
        "profession": "physiotherapist",
        "province": "Enga",
        "qualification": "Bachelor of Physiotherapy",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Thomas",
        "last_name": "Yama",
        "profession": "radiographer",
        "province": "Southern Highlands",
        "qualification": "Bachelor of Medical Imaging",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Maria",
        "last_name": "Kalo",
        "profession": "dentist",
        "province": "NCD",
        "qualification": "Bachelor of Dental Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Andrew",
        "last_name": "Gima",
        "profession": "community_health_worker",
        "province": "Gulf",
        "qualification": "Diploma in Community Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Rose",
        "last_name": "Kapi",
        "profession": "registered_nurse",
        "province": "New Ireland",
        "qualification": "Bachelor of Nursing",
        "institution": "PAU",
        "campus": "Koiari Park Campus",
    },
    {
        "first_name": "Daniel",
        "last_name": "Mena",
        "profession": "doctor",
        "province": "Western",
        "qualification": "Bachelor of Medicine and Bachelor of Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Elizabeth",
        "last_name": "Tari",
        "profession": "midwife",
        "province": "Hela",
        "qualification": "Bachelor of Midwifery",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Joseph",
        "last_name": "Wali",
        "profession": "health_extension_officer",
        "province": "Jiwaka",
        "qualification": "Bachelor of Rural Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Agnes",
        "last_name": "Puri",
        "profession": "medical_laboratory",
        "province": "West New Britain",
        "qualification": "Bachelor of Medical Laboratory Science",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Paul",
        "last_name": "Kua",
        "profession": "pharmacist",
        "province": "Eastern Highlands",
        "qualification": "Bachelor of Pharmacy",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Margaret",
        "last_name": "Aihi",
        "profession": "registered_nurse",
        "province": "Northern",
        "qualification": "Bachelor of Nursing",
        "institution": "PAU",
        "campus": "Koiari Park Campus",
    },
    {
        "first_name": "Henry",
        "last_name": "Kambe",
        "profession": "doctor",
        "province": "Bougainville",
        "qualification": "Bachelor of Medicine and Bachelor of Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Helen",
        "last_name": "Muri",
        "profession": "community_health_worker",
        "province": "Manus",
        "qualification": "Diploma in Community Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Robert",
        "last_name": "Nime",
        "profession": "radiographer",
        "province": "Morobe",
        "qualification": "Bachelor of Medical Imaging",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Catherine",
        "last_name": "Bai",
        "profession": "physiotherapist",
        "province": "Madang",
        "qualification": "Bachelor of Physiotherapy",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Steven",
        "last_name": "Kone",
        "profession": "dentist",
        "province": "NCD",
        "qualification": "Bachelor of Dental Surgery",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Ruth",
        "last_name": "Aru",
        "profession": "registered_nurse",
        "province": "East New Britain",
        "qualification": "Bachelor of Nursing",
        "institution": "PAU",
        "campus": "Koiari Park Campus",
    },
    {
        "first_name": "Mark",
        "last_name": "Tomo",
        "profession": "health_extension_officer",
        "province": "Western Highlands",
        "qualification": "Bachelor of Rural Health",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "Theresa",
        "last_name": "Kila",
        "profession": "midwife",
        "province": "Central",
        "qualification": "Bachelor of Midwifery",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
    {
        "first_name": "James",
        "last_name": "Raka",
        "profession": "pharmacist",
        "province": "New Ireland",
        "qualification": "Bachelor of Pharmacy",
        "institution": "UPNG",
        "campus": "Taurama Campus",
    },
    {
        "first_name": "Sarah",
        "last_name": "Malo",
        "profession": "medical_laboratory",
        "province": "Milne Bay",
        "qualification": "Bachelor of Medical Laboratory Science",
        "institution": "DWU",
        "campus": "Madang Campus",
    },
]


class Command(BaseCommand):
    help = (
        "Create 30 demo existing health workers with expired "
        "medical licenses for renewal testing."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        today = date.today()

        created_users = 0
        created_applications = 0
        created_licenses = 0

        self.stdout.write("")
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Creating expired health worker demo records..."
            )
        )
        self.stdout.write("")

        for index, worker in enumerate(
            HEALTH_WORKERS,
            start=1,
        ):
            email = f"expired.worker{index:02d}@demo.local"
            username = f"expired_worker_{index:02d}"

            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "first_name": worker["first_name"],
                    "last_name": worker["last_name"],
                    "role": "health_worker",
                    "is_active": True,
                },
            )

            if user_created:
                user.set_password("Demo12345!")
                user.save()

                created_users += 1

            else:
                changed = False

                if user.role != "health_worker":
                    user.role = "health_worker"
                    changed = True

                if not user.first_name:
                    user.first_name = worker["first_name"]
                    changed = True

                if not user.last_name:
                    user.last_name = worker["last_name"]
                    changed = True

                if changed:
                    user.save()

            full_name = (
                f"{worker['first_name']} "
                f"{worker['last_name']}"
            )

            application = (
                MedicalLicenseApplication.objects
                .filter(applicant=user)
                .first()
            )

            if application is None:
                application = MedicalLicenseApplication.objects.create(
                    applicant=user,
                    application_type="new",
                    full_name=full_name,
                    date_of_birth=date(
                        1975 + (index % 20),
                        ((index - 1) % 12) + 1,
                        ((index - 1) % 27) + 1,
                    ),
                    gender=(
                        "male"
                        if index % 2
                        else "female"
                    ),
                    nationality="Papua New Guinean",
                    phone_number=f"70{index:06d}",
                    email=email,
                    residential_address=(
                        f"Demo Residential Address {index}"
                    ),
                    province=worker["province"],
                    district="Demo District",
                    profession=worker["profession"],
                    professional_registration_number=(
                        f"PNG-REG-{2018 + (index % 7)}-"
                        f"{index:05d}"
                    ),
                    specialization="General Practice",
                    years_of_experience=(
                        3 + (index % 15)
                    ),
                    qualification=worker["qualification"],
                    institution=worker["institution"],
                    campus=worker["campus"],
                    institution_province="Madang",
                    country_of_qualification="Papua New Guinea",
                    year_started=2010 + (index % 6),
                    year_completed=2014 + (index % 6),
                    graduation_status="graduated",
                    current_employer=(
                        f"Provincial Health Facility {index}"
                    ),
                    position=(
                        worker["qualification"]
                    ),
                    workplace_province=worker["province"],
                    employment_start_date=date(
                        2018 + (index % 6),
                        1,
                        1,
                    ),
                    status="license_generated",
                    submitted_at=(
                        today - timedelta(days=900 + index)
                    ),
                    reviewed_at=(
                        today - timedelta(days=880 + index)
                    ),
                )

                created_applications += 1

            else:
                application.status = "license_generated"
                application.full_name = (
                    application.full_name or full_name
                )
                application.profession = (
                    application.profession
                    or worker["profession"]
                )
                application.province = (
                    application.province
                    or worker["province"]
                )
                application.professional_registration_number = (
                    application.professional_registration_number
                    or f"PNG-REG-{2018 + (index % 7)}-{index:05d}"
                )

                application.save()

            medical_license = (
                MedicalLicense.objects
                .filter(application=application)
                .first()
            )

            if medical_license is None:
                license_number = self._next_license_number()

                issue_date = (
                    today
                    - timedelta(
                        days=730 + (index * 3)
                    )
                )

                expiry_date = (
                    today
                    - timedelta(
                        days=30 + (index * 8)
                    )
                )

                medical_license = MedicalLicense.objects.create(
                    application=application,
                    applicant=user,
                    license_number=license_number,
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    status="expired",
                )

                created_licenses += 1

            else:
                medical_license.applicant = user

                # These are demo expired-license records.
                # Keep the license number unchanged.
                medical_license.status = "expired"

                if medical_license.expiry_date >= today:
                    medical_license.expiry_date = (
                        today
                        - timedelta(days=30 + index)
                    )

                medical_license.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"[{index:02d}/30] "
                    f"{full_name} | "
                    f"{medical_license.license_number} | "
                    f"Expired: "
                    f"{medical_license.expiry_date:%d %b %Y}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Expired health worker demo records are ready."
            )
        )

        self.stdout.write(
            f"Users created: {created_users}"
        )
        self.stdout.write(
            f"Applications created: {created_applications}"
        )
        self.stdout.write(
            f"Licenses created: {created_licenses}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Demo login password for newly created accounts:"
        )
        self.stdout.write(
            self.style.WARNING("Demo12345!")
        )
        self.stdout.write("")
        self.stdout.write(
            "Example login:"
        )
        self.stdout.write(
            "expired.worker01@demo.local"
        )
        self.stdout.write("")

    def _next_license_number(self):
        year = 2025
        sequence = 1

        while True:
            license_number = (
                f"PNG-MED-{year}-{sequence:06d}"
            )

            exists = MedicalLicense.objects.filter(
                license_number=license_number
            ).exists()

            if not exists:
                return license_number

            sequence += 1

