from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Resident


class BarangayProfilingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='testadmin@barangay.gov.ph',
            password='Password123!'
        )

        self.resident1 = Resident.objects.create(
            full_name="Juan Dela Cruz",
            age=40,
            gender="Male",
            civil_status="Married",
            purok="Purok 1 Centro",
            occupation="Engineer",
            is_voter=True
        )

        self.resident2 = Resident.objects.create(
            full_name="Maria Santos",
            age=16,
            gender="Female",
            civil_status="Single",
            purok="Purok 2 Riverside",
            occupation="Student",
            is_voter=False
        )

        self.resident3 = Resident.objects.create(
            full_name="Rodrigo Duterte",
            age=65,
            gender="Male",
            civil_status="Widowed",
            purok="Purok 3 San Jose",
            occupation="Pensioner",
            is_voter=True
        )

    def test_model_properties(self):
        """Test model helper properties and formatted id."""
        self.assertEqual(self.resident1.formatted_id, f"BRGY-{self.resident1.id:04d}")
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
        self.assertContains(response, "digital record")

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
        self.assertContains(dashboard_response, "Total Residents")
        # Check that resident count 3 is rendered
        self.assertEqual(dashboard_response.context['total_residents'], 3)
        self.assertEqual(dashboard_response.context['male_residents'], 2)
        self.assertEqual(dashboard_response.context['female_residents'], 1)
        self.assertEqual(dashboard_response.context['registered_voters'], 2)
        self.assertEqual(dashboard_response.context['minors'], 1)

    def test_resident_case_insensitive_search(self):
        """Search should be case-insensitive for full name, purok, occupation."""
        self.client.login(username='testadmin', password='Password123!')

        # Lowercase search for Juan
        res_juan = self.client.get(reverse('resident_list') + '?q=juan')
        self.assertContains(res_juan, "Juan Dela Cruz")
        self.assertNotContains(res_juan, "Maria Santos")

        # Search by purok
        res_purok = self.client.get(reverse('resident_list') + '?q=riverside')
        self.assertContains(res_purok, "Maria Santos")
        self.assertNotContains(res_purok, "Juan Dela Cruz")

        # Search by occupation
        res_occ = self.client.get(reverse('resident_list') + '?q=engineer')
        self.assertContains(res_occ, "Juan Dela Cruz")

        # Non-matching search
        res_none = self.client.get(reverse('resident_list') + '?q=nonexistentpersonxyz')
        self.assertContains(res_none, "No resident found")

    def test_add_resident_valid_and_invalid(self):
        """Test adding resident with validation."""
        self.client.login(username='testadmin', password='Password123!')

        # Invalid: empty name and negative age
        invalid_res = self.client.post(reverse('resident_create'), {
            'full_name': '',
            'age': -5,
            'gender': 'Male',
            'civil_status': 'Single',
            'purok': 'Purok 1',
        })
        self.assertEqual(invalid_res.status_code, 200)
        self.assertFormError(invalid_res, 'form', 'full_name', 'This field is required.')
        self.assertFormError(invalid_res, 'form', 'age', 'Age cannot be negative.')

        # Valid addition
        valid_res = self.client.post(reverse('resident_create'), {
            'full_name': 'Jose Rizal Mercado',
            'age': 35,
            'gender': 'Male',
            'civil_status': 'Single',
            'purok': 'Purok 1 Centro',
            'occupation': 'Writer / Doctor',
            'is_voter': True,
            'contact_number': '0912-333-4444'
        })
        self.assertEqual(valid_res.status_code, 302)
        self.assertTrue(Resident.objects.filter(full_name='Jose Rizal Mercado').exists())

    def test_update_resident(self):
        """Test editing resident information."""
        self.client.login(username='testadmin', password='Password123!')

        response = self.client.post(reverse('resident_update', kwargs={'pk': self.resident1.pk}), {
            'full_name': 'Juan Dela Cruz Jr.',
            'age': 41,
            'gender': 'Male',
            'civil_status': 'Married',
            'purok': 'Purok 1 Centro (Updated)',
            'occupation': 'Senior Engineer',
            'is_voter': True,
        })
        self.assertEqual(response.status_code, 302)
        self.resident1.refresh_from_db()
        self.assertEqual(self.resident1.full_name, 'Juan Dela Cruz Jr.')
        self.assertEqual(self.resident1.age, 41)
        self.assertEqual(self.resident1.occupation, 'Senior Engineer')

    def test_delete_resident_post_only(self):
        """Test secure POST deletion and confirmation view on GET."""
        self.client.login(username='testadmin', password='Password123!')

        # GET should render confirmation page without deleting
        get_res = self.client.get(reverse('resident_delete', kwargs={'pk': self.resident2.pk}))
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, "Are you sure you want to delete this resident?")
        self.assertTrue(Resident.objects.filter(pk=self.resident2.pk).exists())

        # POST deletes the record
        post_res = self.client.post(reverse('resident_delete', kwargs={'pk': self.resident2.pk}))
        self.assertEqual(post_res.status_code, 302)
        self.assertFalse(Resident.objects.filter(pk=self.resident2.pk).exists())

    def test_population_report_view(self):
        """Population report computes statistics and supplies chart data."""
        self.client.login(username='testadmin', password='Password123!')
        response = self.client.get(reverse('population_report'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Population Report")
        self.assertIn('chart_data_json', response.context)
        self.assertEqual(response.context['total_residents'], 3)

    def test_logout(self):
        """Test admin logout."""
        self.client.login(username='testadmin', password='Password123!')
        response = self.client.get(reverse('admin_logout'))
        self.assertEqual(response.status_code, 302)
        # Attempt to access dashboard now
        dash_res = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_res.status_code, 302)
