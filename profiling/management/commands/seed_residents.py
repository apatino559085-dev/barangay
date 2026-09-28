from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiling.models import Resident


class Command(BaseCommand):
    help = "Seeds initial admin, barangay staff official, and realistic household profiling records."

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
        else:
            self.stdout.write(self.style.NOTICE("Administrator 'admin' already exists."))

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
        else:
            self.stdout.write(self.style.NOTICE("Staff official 'staff' already exists."))

        # 3. Seed Realistic Household Profiling Records
        # Reset and populate clean household data if needed
        if Resident.objects.count() == 0:
            sample_households = [
                # Household 1 - Dela Cruz Family (4 members in Purok 1 Centro)
                {"full_name": "Juan Dela Cruz", "age": 42, "gender": "Male", "civil_status": "Married", "purok": "Purok 1 Centro", "occupation": "Civil Engineer", "contact_number": "0917-123-4567", "household_number": "HH-001", "household_head": "Juan Dela Cruz", "household_members_count": 4, "relationship_to_head": "Head"},
                {"full_name": "Maria Corazon Dela Cruz", "age": 39, "gender": "Female", "civil_status": "Married", "purok": "Purok 1 Centro", "occupation": "Public School Teacher", "contact_number": "0918-234-5678", "household_number": "HH-001", "household_head": "Juan Dela Cruz", "household_members_count": 4, "relationship_to_head": "Spouse"},
                {"full_name": "Gabriel Santos Dela Cruz", "age": 14, "gender": "Male", "civil_status": "Single", "purok": "Purok 1 Centro", "occupation": "High School Student", "contact_number": "", "household_number": "HH-001", "household_head": "Juan Dela Cruz", "household_members_count": 4, "relationship_to_head": "Son"},
                {"full_name": "Angelica Santos Dela Cruz", "age": 9, "gender": "Female", "civil_status": "Single", "purok": "Purok 1 Centro", "occupation": "Elementary Student", "contact_number": "", "household_number": "HH-001", "household_head": "Juan Dela Cruz", "household_members_count": 4, "relationship_to_head": "Daughter"},

                # Household 2 - Bautista Family (3 members in Purok 2 Riverside)
                {"full_name": "Elena Morales Bautista", "age": 63, "gender": "Female", "civil_status": "Widowed", "purok": "Purok 2 Riverside", "occupation": "Sari-Sari Store Owner", "contact_number": "0920-456-7890", "household_number": "HH-002", "household_head": "Elena Morales Bautista", "household_members_count": 3, "relationship_to_head": "Head"},
                {"full_name": "Clarissa Joy Bautista", "age": 28, "gender": "Female", "civil_status": "Single", "purok": "Purok 2 Riverside", "occupation": "Call Center Agent", "contact_number": "0932-678-4321", "household_number": "HH-002", "household_head": "Elena Morales Bautista", "household_members_count": 3, "relationship_to_head": "Daughter"},
                {"full_name": "Joshua Morales Bautista", "age": 16, "gender": "Male", "civil_status": "Single", "purok": "Purok 2 Riverside", "occupation": "Junior High Student", "contact_number": "", "household_number": "HH-002", "household_head": "Elena Morales Bautista", "household_members_count": 3, "relationship_to_head": "Son"},

                # Household 3 - Ramos Family (2 members in Purok 2 Riverside)
                {"full_name": "Rodrigo Duterte Ramos", "age": 68, "gender": "Male", "civil_status": "Widowed", "purok": "Purok 2 Riverside", "occupation": "Retired Barangay Official", "contact_number": "0919-345-6789", "household_number": "HH-003", "household_head": "Rodrigo Duterte Ramos", "household_members_count": 2, "relationship_to_head": "Head"},
                {"full_name": "Emilio Ramos", "age": 35, "gender": "Male", "civil_status": "Single", "purok": "Purok 2 Riverside", "occupation": "Carpenter", "contact_number": "0931-567-5432", "household_number": "HH-003", "household_head": "Rodrigo Duterte Ramos", "household_members_count": 2, "relationship_to_head": "Son"},

                # Household 4 - Mendoza Family (5 members in Purok 5 Maharlika)
                {"full_name": "Danilo Cruz Mendoza", "age": 55, "gender": "Male", "civil_status": "Married", "purok": "Purok 5 Maharlika", "occupation": "Tricycle Driver", "contact_number": "0925-901-2345", "household_number": "HH-004", "household_head": "Danilo Cruz Mendoza", "household_members_count": 5, "relationship_to_head": "Head"},
                {"full_name": "Josefina Mercado Mendoza", "age": 52, "gender": "Female", "civil_status": "Married", "purok": "Purok 5 Maharlika", "occupation": "Homemaker", "contact_number": "0926-012-3456", "household_number": "HH-004", "household_head": "Danilo Cruz Mendoza", "household_members_count": 5, "relationship_to_head": "Spouse"},
                {"full_name": "Daniel Padilla Mendoza", "age": 19, "gender": "Male", "civil_status": "Single", "purok": "Purok 5 Maharlika", "occupation": "College Student", "contact_number": "0925-111-2233", "household_number": "HH-004", "household_head": "Danilo Cruz Mendoza", "household_members_count": 5, "relationship_to_head": "Son"},
                {"full_name": "Daphne Mercado Mendoza", "age": 15, "gender": "Female", "civil_status": "Single", "purok": "Purok 5 Maharlika", "occupation": "Student", "contact_number": "", "household_number": "HH-004", "household_head": "Danilo Cruz Mendoza", "household_members_count": 5, "relationship_to_head": "Daughter"},
                {"full_name": "Luzviminda Cruz", "age": 78, "gender": "Female", "civil_status": "Widowed", "purok": "Purok 5 Maharlika", "occupation": "Senior Pensioner", "contact_number": "", "household_number": "HH-004", "household_head": "Danilo Cruz Mendoza", "household_members_count": 5, "relationship_to_head": "Mother"},

                # Household 5 - Villanueva Family (4 members in Purok 7 Ilaya)
                {"full_name": "Fernando Poe Villanueva", "age": 48, "gender": "Male", "civil_status": "Married", "purok": "Purok 7 Ilaya", "occupation": "Fisherman / Farmer", "contact_number": "0929-345-7654", "household_number": "HH-005", "household_head": "Fernando Poe Villanueva", "household_members_count": 4, "relationship_to_head": "Head"},
                {"full_name": "Rosario Alcantara Villanueva", "age": 45, "gender": "Female", "civil_status": "Married", "purok": "Purok 7 Ilaya", "occupation": "Fish Vendor", "contact_number": "0930-456-6543", "household_number": "HH-005", "household_head": "Fernando Poe Villanueva", "household_members_count": 4, "relationship_to_head": "Spouse"},
                {"full_name": "Sophia Nicole Villanueva", "age": 17, "gender": "Female", "civil_status": "Single", "purok": "Purok 7 Ilaya", "occupation": "Senior High Student", "contact_number": "", "household_number": "HH-005", "household_head": "Fernando Poe Villanueva", "household_members_count": 4, "relationship_to_head": "Daughter"},
                {"full_name": "Carlo James Villanueva", "age": 12, "gender": "Male", "civil_status": "Single", "purok": "Purok 7 Ilaya", "occupation": "Grade School Student", "contact_number": "", "household_number": "HH-005", "household_head": "Fernando Poe Villanueva", "household_members_count": 4, "relationship_to_head": "Son"},
            ]

            for data in sample_households:
                Resident.objects.create(**data)

            self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(sample_households)} household profiling records!"))
