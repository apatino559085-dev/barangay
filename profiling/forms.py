from django import forms
from django.contrib.auth.models import User
from .models import (
    Household, Resident, ResidentConcern, UserProfile,
    PUROK_CHOICES, HOUSE_TYPE_CHOICES, HOUSING_OWNERSHIP_CHOICES,
    WATER_SOURCE_CHOICES, ELECTRICITY_CHOICES, TOILET_FACILITY_CHOICES,
    HOUSEHOLD_STATUS_CHOICES, VERIFICATION_STATUS_CHOICES,
    GENDER_CHOICES, CIVIL_STATUS_CHOICES, RELATIONSHIP_CHOICES,
    EDUCATION_CHOICES, EMPLOYMENT_CHOICES, RESIDENCY_STATUS_CHOICES
)


# ==========================================
# 1. HOUSEHOLD PROFILING FORM
# ==========================================
class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = [
            'household_number',
            'purok',
            'complete_address',
            'head_name',
            'contact_number',
            'members_count',
            'house_type',
            'housing_ownership',
            'water_source',
            'electricity',
            'toilet_facility',
            'household_status',
        ]
        widgets = {
            'household_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. HH-2026-001',
                'required': True,
            }),
            'purok': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'complete_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'House / Block / Lot / Street, Barangay Hall vicinity',
                'required': True,
            }),
            'head_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name of Household Head / Family Head',
                'required': True,
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09XX-XXX-XXXX',
            }),
            'members_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'placeholder': 'e.g. 4',
                'required': True,
            }),
            'house_type': forms.Select(attrs={'class': 'form-select'}),
            'housing_ownership': forms.Select(attrs={'class': 'form-select'}),
            'water_source': forms.Select(attrs={'class': 'form-select'}),
            'electricity': forms.Select(attrs={'class': 'form-select'}),
            'toilet_facility': forms.Select(attrs={'class': 'form-select'}),
            'household_status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_household_number(self):
        number = self.cleaned_data.get('household_number', '').strip()
        if not number:
            raise forms.ValidationError("Household number is required.")
        # Check uniqueness on creation or edit
        qs = Household.objects.filter(household_number__iexact=number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Household number '{number}' already exists in the system.")
        return number

    def clean_members_count(self):
        count = self.cleaned_data.get('members_count')
        if count is None or count < 1:
            raise forms.ValidationError("Number of members must be at least 1.")
        return count


# ==========================================
# 2. RESIDENT FORM (Tied to Household)
# ==========================================
class ResidentForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            'household',
            'first_name',
            'middle_name',
            'last_name',
            'birthdate',
            'age',
            'sex',
            'civil_status',
            'relationship_to_head',
            'educational_attainment',
            'occupation',
            'employment_status',
            'contact_number',
            'residency_status',
            'is_pwd',
            'is_4ps',
            'is_single_parent',
            'is_voter',
            'voter_id',
            'blood_type',
        ]
        widgets = {
            'household': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name (e.g. Juan)',
                'required': True,
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Middle Name (e.g. Santos)',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name (e.g. Dela Cruz)',
                'required': True,
            }),
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '130',
                'placeholder': 'Age',
                'required': True,
            }),
            'sex': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'civil_status': forms.Select(attrs={'class': 'form-select'}),
            'relationship_to_head': forms.Select(attrs={'class': 'form-select'}),
            'educational_attainment': forms.Select(attrs={'class': 'form-select'}),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Farmer, Teacher, Driver, Student',
            }),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09XX-XXX-XXXX',
            }),
            'residency_status': forms.Select(attrs={'class': 'form-select'}),
            'is_pwd': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_4ps': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_single_parent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_voter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'voter_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Voter ID No. (optional)'}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. O+, A+, B-'}),
        }

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name', '').strip()
        if not name:
            raise forms.ValidationError("First name is required.")
        return name

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name', '').strip()
        if not name:
            raise forms.ValidationError("Last name is required.")
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is None or age < 0:
            raise forms.ValidationError("Please provide a valid age.")
        if age > 130:
            raise forms.ValidationError("Age cannot exceed 130 years.")
        return age


# ==========================================
# 3. ADMIN PROFILE VERIFICATION FORM
# ==========================================
class HouseholdVerificationForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ['verification_status', 'admin_remarks']
        widgets = {
            'verification_status': forms.Select(
                choices=[
                    ('Approved', 'Approve Profile (Mark as Verified)'),
                    ('Returned for Correction', 'Return for Correction (Request Revisions)'),
                ],
                attrs={'class': 'form-select fw-semibold'}
            ),
            'admin_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter remarks or correction instructions for the barangay staff...',
            }),
        }


# ==========================================
# 4. RESIDENT CONCERN FORM (Secondary Feature)
# ==========================================
class ResidentConcernForm(forms.ModelForm):
    class Meta:
        model = ResidentConcern
        fields = [
            'complainant_name',
            'contact_number',
            'purok',
            'subject',
            'category',
            'description',
        ]
        widgets = {
            'complainant_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resident / Complainant Full Name',
                'required': True,
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '09XX-XXX-XXXX',
            }),
            'purok': forms.Select(
                choices=PUROK_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief Subject / Issue Title',
                'required': True,
            }),
            'category': forms.Select(
                choices=[
                    ('General Concern', 'General Concern'),
                    ('Sanitation / Drainage', 'Sanitation & Drainage'),
                    ('Street Light / Road', 'Street Light / Road Maintenance'),
                    ('Peace & Order', 'Peace & Order / Noise'),
                    ('Health & Social Welfare', 'Health & Social Welfare'),
                    ('Other', 'Other Request / Inquiry'),
                ],
                attrs={'class': 'form-select'}
            ),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description of the concern or incident...',
                'required': True,
            }),
        }


# ==========================================
# 5. USER MANAGEMENT FORM (Admin Only)
# ==========================================
class UserCreateForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=[('Staff', 'Barangay Staff'), ('Admin', 'Barangay Administrator')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='Staff'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter initial password'}),
        required=True
    )
    contact_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact number'})
    )
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Purok Profiler / Admin Assistant'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        role = self.cleaned_data.get('role', 'Staff')
        if role == 'Admin':
            user.is_superuser = True
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = True
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.contact_number = self.cleaned_data.get('contact_number', '')
            profile.designation = self.cleaned_data.get('designation', '')
            profile.save()
        return user
