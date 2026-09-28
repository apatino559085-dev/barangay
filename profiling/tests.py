from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from profiling.models import Resident, Household


class BarangayProfilingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@barangay.gov.ph',
            password='Password123!'
        )

        self.household1 = Household.objects.create(
            household_number="HH-TEST-01",
            purok="Purok 1",
            complete_address="123 Test St",
            head_name="Juan Dela Cruz",
            verification_status="Approved"
        )

        self.household2 = Household.objects.create(
            household_number="HH-TEST-02",
            purok="Purok 2 Riverside",
            complete_address="45 Riverside St",
            head_name="Maria Santos",
            verification_status="Approved"
        )

        self.resident1 = Resident.objects.create(
            household=self.household1,
            first_name="Juan",
            last_name="Dela Cruz",
            age=40,
            sex="Male",
            gender="Male",
            civil_status="Married",
            purok="Purok 1",
            occupation="Engineer",
            is_voter=True
        )

        self.resident2 = Resident.objects.create(
            household=self.household2,
            first_name="Maria",
            last_name="Santos",
            age=16,
            sex="Female",
            gender="Female",
            civil_status="Single",
            purok="Purok 2 Riverside",
            occupation="Student",
            is_voter=False
        )

        self.resident3 = Resident.objects.create(
            household=self.household1,
            first_name="Rodrigo",
            last_name="Duterte",
            age=65,
            sex="Male",
            gender="Male",
            civil_status="Widowed",
            purok="Purok 3 San Jose",
            occupation="Pensioner",
            is_voter=True
        )

    def test_model_properties(self):
        """Test model helper properties and formatted id."""
        self.assertEqual(self.resident1.formatted_id, f"RES-{self.resident1.id:04d}")
        self.assertFalse(self.resident1.is_minor)
        self.assertFalse(self.resident1.is_senior)

        self.assertTrue(self.resident2.is_minor)
        self.assertFalse(self.resident2.is_senior)

        self.assertFalse(self.resident3.is_minor)
        self.assertTrue(self.resident3.is_senior)

    def test_landing_page_accessible(self):
        """Public landing page should be accessible without logging in."""
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Barangay")

    def test_protected_views_require_login(self):
        """Unauthenticated requests to protected endpoints should redirect to login."""
        protected_urls = [
            reverse('dashboard'),
            reverse('resident_list'),
            reverse('resident_create'),
            reverse('resident_detail', kwargs={'pk': self.resident1.pk}),
            reverse('resident_update', kwargs={'pk': self.resident1.pk}),
            reverse('resident_delete', kwargs={'pk': self.resident1.pk}),
            reverse('population_report'),
            reverse('admin_profile'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)

    def test_admin_login_and_dashboard(self):
        """Admin can log in and view dashboard statistics."""
        response = self.client.post(reverse('admin_login'), {
            'username': 'testadmin',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)

        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(dashboard_response.context['total_residents'], 3)
        self.assertEqual(dashboard_response.context['male_residents'], 2)
        self.assertEqual(dashboard_response.context['female_residents'], 1)

    def test_resident_case_insensitive_search(self):
        """Search should be case-insensitive for full name, purok, occupation."""
        self.client.login(username='testadmin', password='Password123!')

        # Lowercase search for Juan
        res_juan = self.client.get(reverse('resident_list') + '?q=juan')
        self.assertContains(res_juan, "Juan Dela Cruz")

        # Search by purok
        res_purok = self.client.get(reverse('resident_list') + '?q=riverside')
        self.assertContains(res_purok, "Maria Santos")

        # Search by occupation
        res_occ = self.client.get(reverse('resident_list') + '?q=engineer')
        self.assertContains(res_occ, "Juan Dela Cruz")

    def test_add_resident_valid_and_invalid(self):
        """Test adding resident with validation."""
        self.client.login(username='testadmin', password='Password123!')

        # Invalid: empty first_name
        invalid_res = self.client.post(reverse('resident_create'), {
            'household': self.household1.pk,
            'first_name': '',
            'last_name': 'Sample',
            'age': 20,
            'sex': 'Male',
            'civil_status': 'Single',
            'relationship_to_head': 'Head',
            'educational_attainment': 'High School Graduate',
            'employment_status': 'Employed (Private)',
            'residency_status': 'Permanent Resident',
        })
        self.assertEqual(invalid_res.status_code, 200)
        self.assertFormError(invalid_res, 'form', 'first_name', 'First name is required.')

        # Valid addition
        valid_res = self.client.post(reverse('resident_create'), {
            'household': self.household1.pk,
            'first_name': 'Jose',
            'last_name': 'Rizal',
            'age': 35,
            'sex': 'Male',
            'civil_status': 'Single',
            'relationship_to_head': 'Head',
            'educational_attainment': 'College Graduate',
            'occupation': 'Writer',
            'employment_status': 'Employed (Private)',
            'residency_status': 'Permanent Resident',
            'is_voter': True,
        })
        self.assertEqual(valid_res.status_code, 302)
        self.assertTrue(Resident.objects.filter(first_name='Jose', last_name='Rizal').exists())

    def test_update_resident(self):
        """Test editing resident information."""
        self.client.login(username='testadmin', password='Password123!')

        response = self.client.post(reverse('resident_update', kwargs={'pk': self.resident1.pk}), {
            'household': self.household1.pk,
            'first_name': 'Juan Jr.',
            'last_name': 'Dela Cruz',
            'age': 41,
            'sex': 'Male',
            'civil_status': 'Married',
            'relationship_to_head': 'Head',
            'educational_attainment': 'High School Graduate',
            'occupation': 'Senior Engineer',
            'employment_status': 'Employed (Private)',
            'residency_status': 'Permanent Resident',
            'is_voter': True,
        })
        self.assertEqual(response.status_code, 302)
        self.resident1.refresh_from_db()
        self.assertEqual(self.resident1.first_name, 'Juan Jr.')
        self.assertEqual(self.resident1.age, 41)

    def test_delete_resident_post_only(self):
        """Test secure POST deletion and confirmation view on GET."""
        self.client.login(username='testadmin', password='Password123!')

        get_res = self.client.get(reverse('resident_delete', kwargs={'pk': self.resident2.pk}))
        self.assertEqual(get_res.status_code, 200)

        post_res = self.client.post(reverse('resident_delete', kwargs={'pk': self.resident2.pk}))
        self.assertEqual(post_res.status_code, 302)
        self.assertFalse(Resident.objects.filter(pk=self.resident2.pk).exists())

    def test_population_report_view(self):
        """Population report computes statistics and supplies chart data."""
        self.client.login(username='testadmin', password='Password123!')
        response = self.client.get(reverse('population_report'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_residents'], 3)
