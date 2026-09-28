from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiling.models import Household, Resident


class Command(BaseCommand):
    help = "Seeds initial admin, barangay staff official, households, and realistic resident profiling records."

    def handle(self, *args, **options):
        # 1. Administrator User
        admin_user, admin_created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@barangay.gov.ph",
                "first_name": "Barangay",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if admin_created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Barangay Administrator: admin / admin123"))

        # 2. Field Staff / Barangay Official User
        staff_user, staff_created = User.objects.get_or_create(
            username="staff",
            defaults={
                "email": "staff@barangay.gov.ph",
                "first_name": "Barangay",
                "last_name": "Official",
                "is_staff": True,
                "is_superuser": False,
            }
        )
        if staff_created:
            staff_user.set_password("staff123")
            staff_user.save()
            self.stdout.write(self.style.SUCCESS("Created Barangay Staff / Official: staff / staff123"))

        # 3. Seed Households and Residents
        if Household.objects.count() == 0:
            households_data = [
                {
                    "number": "HH-001", "purok": "Purok 1", "address": "123 Centro St., Purok 1", "head": "Juan Dela Cruz",
                    "members": [
                        {"first": "Juan", "middle": "Santos", "last": "Dela Cruz", "age": 42, "sex": "Male", "status": "Married", "rel": "Head", "occ": "Civil Engineer", "phone": "0917-123-4567", "voter": True, "voter_id": "V-12345"},
                        {"first": "Maria Corazon", "middle": "Santos", "last": "Dela Cruz", "age": 39, "sex": "Female", "status": "Married", "rel": "Spouse", "occ": "Public School Teacher", "phone": "0918-234-5678", "voter": True},
                        {"first": "Gabriel", "middle": "Santos", "last": "Dela Cruz", "age": 19, "sex": "Male", "status": "Single", "rel": "Son", "occ": "College Student", "phone": "0918-999-0000", "voter": True},
                        {"first": "Angelica", "middle": "Santos", "last": "Dela Cruz", "age": 9, "sex": "Female", "status": "Single", "rel": "Daughter", "occ": "Elementary Student", "phone": "", "voter": False},
                    ]
                },
                {
                    "number": "HH-002", "purok": "Purok 2", "address": "45 Riverside Road, Purok 2", "head": "Elena Morales Bautista",
                    "members": [
                        {"first": "Elena", "middle": "Morales", "last": "Bautista", "age": 63, "sex": "Female", "status": "Widowed", "rel": "Head", "occ": "Sari-Sari Store Owner", "phone": "0920-456-7890", "voter": True, "single_parent": True, "pwd": True},
                        {"first": "Clarissa Joy", "middle": "Morales", "last": "Bautista", "age": 28, "sex": "Female", "status": "Single", "rel": "Daughter", "occ": "Call Center Agent", "phone": "0932-678-4321", "voter": True},
                        {"first": "Joshua", "middle": "Morales", "last": "Bautista", "age": 16, "sex": "Male", "status": "Single", "rel": "Son", "occ": "Junior High Student", "phone": "", "voter": False},
                    ]
                },
                {
                    "number": "HH-003", "purok": "Purok 5", "address": "88 Maharlika Highway, Purok 5", "head": "Danilo Cruz Mendoza",
                    "members": [
                        {"first": "Danilo", "middle": "Cruz", "last": "Mendoza", "age": 55, "sex": "Male", "status": "Married", "rel": "Head", "occ": "Tricycle Driver", "phone": "0925-901-2345", "voter": True, "four_ps": True},
                        {"first": "Josefina", "middle": "Mercado", "last": "Mendoza", "age": 52, "sex": "Female", "status": "Married", "rel": "Spouse", "occ": "Homemaker", "phone": "0926-012-3456", "voter": True, "four_ps": True},
                        {"first": "Daniel", "middle": "Mercado", "last": "Mendoza", "age": 21, "sex": "Male", "status": "Single", "rel": "Son", "occ": "College Student", "phone": "0925-111-2233", "voter": True},
                        {"first": "Luzviminda", "middle": "Cruz", "last": "Mendoza", "age": 78, "sex": "Female", "status": "Widowed", "rel": "Mother", "occ": "Senior Pensioner", "phone": "", "voter": True, "pwd": True},
                    ]
                }
            ]

            for hh_info in households_data:
                hh = Household.objects.create(
                    household_number=hh_info["number"],
                    purok=hh_info["purok"],
                    complete_address=hh_info["address"],
                    head_name=hh_info["head"],
                    members_count=len(hh_info["members"]),
                    verification_status='Approved',
                    profiled_by=admin_user,
                    verified_by=admin_user
                )

                for m in hh_info["members"]:
                    Resident.objects.create(
                        household=hh,
                        first_name=m["first"],
                        middle_name=m["middle"],
                        last_name=m["last"],
                        age=m["age"],
                        sex=m["sex"],
                        gender=m["sex"],
                        civil_status=m["status"],
                        relationship_to_head=m["rel"],
                        occupation=m["occ"],
                        contact_number=m["phone"],
                        is_voter=m.get("voter", False),
                        voter_id=m.get("voter_id", ""),
                        is_4ps=m.get("four_ps", False),
                        is_pwd=m.get("pwd", False),
                        is_single_parent=m.get("single_parent", False),
                        purok=hh_info["purok"],
                        household_number=hh_info["number"],
                        household_head=hh_info["head"]
                    )

            self.stdout.write(self.style.SUCCESS("Successfully seeded sample households and residents!"))
