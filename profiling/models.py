from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Choices for Purok
PUROK_CHOICES = [
    ('Purok 1', 'Purok 1'),
    ('Purok 2', 'Purok 2'),
    ('Purok 3', 'Purok 3'),
    ('Purok 4', 'Purok 4'),
    ('Purok 5', 'Purok 5'),
    ('Purok 6', 'Purok 6'),
    ('Purok 7', 'Purok 7'),
    ('Purok 8', 'Purok 8'),
    ('Purok 9', 'Purok 9'),
    ('Purok 10', 'Purok 10'),
]

# Housing characteristics
HOUSE_TYPE_CHOICES = [
    ('Concrete', 'Concrete'),
    ('Semi-Concrete', 'Semi-Concrete'),
    ('Wood', 'Wood / Timber'),
    ('Bamboo / Light Materials', 'Bamboo / Nipa / Light Materials'),
    ('Makeshift / Salvaged', 'Makeshift / Salvaged Materials'),
]

HOUSING_OWNERSHIP_CHOICES = [
    ('Owned (House & Lot)', 'Owned (House & Lot)'),
    ('Owned House, Rented Lot', 'Owned House, Rented Lot'),
    ('Rented', 'Rented'),
    ('Living with Relatives (Rent-free)', 'Living with Relatives (Rent-free)'),
    ('Rent-free with Consent', 'Rent-free with Owner Consent'),
    ('Informal Settler', 'Informal Settler'),
]

WATER_SOURCE_CHOICES = [
    ('Level III - Piped Water Connection', 'Level III - Piped Water Connection'),
    ('Level II - Communal Faucet / Deep Well', 'Level II - Communal Faucet / Deep Well'),
    ('Level I - Protected Well / Spring', 'Level I - Protected Well / Spring'),
    ('Water Refilling Station / Mineral', 'Water Refilling Station / Mineral'),
    ('Shared / Dug Well', 'Shared / Dug Well'),
]

ELECTRICITY_CHOICES = [
    ('Legal Connection (Utility)', 'Legal Connection (Utility)'),
    ('Shared Connection / Sub-meter', 'Shared Connection / Sub-meter'),
    ('Solar Power', 'Solar Power'),
    ('Generator', 'Generator'),
    ('None / Kerosene / Candle', 'None / Kerosene / Candle'),
]

TOILET_FACILITY_CHOICES = [
    ('Water-sealed Flush', 'Water-sealed Flush (Sewerage/Septic)'),
    ('Pour-flush Toilet', 'Pour-flush Toilet'),
    ('Ventilated Improved Pit (VIP)', 'Ventilated Improved Pit (VIP) Latrine'),
    ('Open Pit Latrine', 'Open Pit Latrine'),
    ('Shared / Communal Toilet', 'Shared / Communal Toilet'),
    ('No Toilet Facility', 'No Toilet Facility'),
]

HOUSEHOLD_STATUS_CHOICES = [
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
    ('Relocated', 'Relocated'),
]

VERIFICATION_STATUS_CHOICES = [
    ('Draft', 'Draft'),
    ('Pending Verification', 'Pending Verification'),
    ('Approved', 'Approved'),
    ('Returned for Correction', 'Returned for Correction'),
]

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

CIVIL_STATUS_CHOICES = [
    ('Single', 'Single'),
    ('Married', 'Married'),
    ('Widowed', 'Widowed'),
    ('Separated', 'Separated'),
    ('Divorced', 'Divorced'),
    ('Live-in / Common-law', 'Live-in / Common-law'),
]

RELATIONSHIP_CHOICES = [
    ('Head', 'Household Head'),
    ('Spouse', 'Spouse'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
    ('Father', 'Father'),
    ('Mother', 'Mother'),
    ('Brother', 'Brother'),
    ('Sister', 'Sister'),
    ('Grandfather', 'Grandfather'),
    ('Grandmother', 'Grandmother'),
    ('Grandson', 'Grandson'),
    ('Granddaughter', 'Granddaughter'),
    ('Relative', 'Other Relative'),
    ('Non-Relative', 'Non-Relative / Boarder / Househelp'),
]

EDUCATION_CHOICES = [
    ('No Formal Education', 'No Formal Education'),
    ('Elementary Undergraduate', 'Elementary Undergraduate'),
    ('Elementary Graduate', 'Elementary Graduate'),
    ('High School Undergraduate', 'High School Undergraduate'),
    ('High School Graduate', 'High School Graduate'),
    ('Senior High School', 'Senior High School'),
    ('Vocational / TVET', 'Vocational / TVET'),
    ('College Undergraduate', 'College Undergraduate'),
    ('College Graduate', 'College Graduate (Bachelor)'),
    ('Post-Graduate', 'Post-Graduate (Master / Doctorate)'),
]

EMPLOYMENT_CHOICES = [
    ('Employed (Private)', 'Employed (Private)'),
    ('Employed (Government)', 'Employed (Government)'),
    ('Self-Employed / Business', 'Self-Employed / Business'),
    ('Informal / Daily Wage', 'Informal / Daily Wage'),
    ('Unemployed', 'Unemployed'),
    ('Student', 'Student'),
    ('Retired / Pensioner', 'Retired / Pensioner'),
    ('Homemaker / Housewife', 'Homemaker / Housewife'),
    ('OFW', 'Overseas Filipino Worker (OFW)'),
]

RESIDENCY_STATUS_CHOICES = [
    ('Permanent Resident', 'Permanent Resident'),
    ('Temporary / Transient', 'Temporary / Transient'),
    ('Transferred Out', 'Transferred Out'),
    ('Deceased', 'Deceased'),
]


# ==========================================
# 1. USER PROFILE (Role-based access: Admin vs Staff)
# ==========================================
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Barangay Administrator'),
        ('Staff', 'Barangay Staff'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Staff', verbose_name="Role")
    full_name = models.CharField(max_length=150, blank=True, verbose_name="Full Name")
    contact_number = models.CharField(max_length=30, blank=True, default="", verbose_name="Contact Number")
    designation = models.CharField(max_length=100, blank=True, default="Barangay Staff", verbose_name="Designation")

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.user.is_superuser or self.role == 'Admin'

    @property
    def is_staff_member(self):
        return self.role == 'Staff' or self.user.is_staff


# Signal to create or save UserProfile automatically
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'Admin' if instance.is_superuser else 'Staff'
        UserProfile.objects.create(
            user=instance,
            role=role,
            full_name=instance.get_full_name() or instance.username,
            designation='Barangay Administrator' if instance.is_superuser else 'Barangay Staff'
        )
    else:
        if hasattr(instance, 'profile'):
            if instance.is_superuser and instance.profile.role != 'Admin':
                instance.profile.role = 'Admin'
                instance.profile.save()


# ==========================================
# 2. HOUSEHOLD PROFILING MODEL
# ==========================================
class Household(models.Model):
    household_number = models.CharField(max_length=50, unique=True, verbose_name="Household No. / ID")
    purok = models.CharField(max_length=100, choices=PUROK_CHOICES, verbose_name="Purok")
    complete_address = models.CharField(max_length=255, verbose_name="Complete Address")
    head_name = models.CharField(max_length=150, verbose_name="Householder / Head of Family")
    contact_number = models.CharField(max_length=30, blank=True, default="", verbose_name="Contact Number")
    members_count = models.PositiveIntegerField(default=1, verbose_name="Number of Household Members")

    # Housing & Living Amenities
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPE_CHOICES, default='Concrete', verbose_name="Type of House")
    housing_ownership = models.CharField(max_length=50, choices=HOUSING_OWNERSHIP_CHOICES, default='Owned (House & Lot)', verbose_name="Housing Ownership")
    water_source = models.CharField(max_length=60, choices=WATER_SOURCE_CHOICES, default='Level III - Piped Water Connection', verbose_name="Water Source")
    electricity = models.CharField(max_length=50, choices=ELECTRICITY_CHOICES, default='Legal Connection (Utility)', verbose_name="Electricity")
    toilet_facility = models.CharField(max_length=60, choices=TOILET_FACILITY_CHOICES, default='Water-sealed Flush', verbose_name="Toilet Facility")

    # Household Status & Verification Workflow
    household_status = models.CharField(max_length=30, choices=HOUSEHOLD_STATUS_CHOICES, default='Active', verbose_name="Household Status")
    verification_status = models.CharField(
        max_length=30,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Draft',
        verbose_name="Verification Status"
    )
    admin_remarks = models.TextField(blank=True, default="", verbose_name="Admin Remarks / Correction Notes")

    # Audit & Staff Tracking
    profiled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiled_households', verbose_name="Profiled By")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_households', verbose_name="Verified By")
    date_profiled = models.DateTimeField(auto_now_add=True, verbose_name="Date Profiled")
    date_verified = models.DateTimeField(null=True, blank=True, verbose_name="Date Verified")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Date Updated")

    class Meta:
        ordering = ['-date_profiled']
        verbose_name = "Household Profile"
        verbose_name_plural = "Household Profiles"

    def __str__(self):
        return f"{self.household_number} - {self.head_name} ({self.purok})"

    @property
    def is_verified(self):
        return self.verification_status == 'Approved'

    @property
    def registered_members_count(self):
        return self.residents.count()

    @property
    def status_badge_class(self):
        mapping = {
            'Draft': 'secondary',
            'Pending Verification': 'warning text-dark',
            'Approved': 'success',
            'Returned for Correction': 'danger',
        }
        return mapping.get(self.verification_status, 'secondary')


# ==========================================
# 3. RESIDENT INFORMATION MODEL (One Household -> Many Residents)
# ==========================================
class Resident(models.Model):
    resident_id = models.CharField(max_length=50, blank=True, default="", verbose_name="Resident ID")
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='residents', null=True, blank=True, verbose_name="Household")

    first_name = models.CharField(max_length=80, blank=True, default="", verbose_name="First Name")
    middle_name = models.CharField(max_length=80, blank=True, default="", verbose_name="Middle Name")
    last_name = models.CharField(max_length=80, blank=True, default="", verbose_name="Last Name")
    full_name = models.CharField(max_length=200, blank=True, default="", verbose_name="Full Name")

    birthdate = models.DateField(null=True, blank=True, verbose_name="Birth Date")
    age = models.PositiveIntegerField(default=0, verbose_name="Age")
    sex = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male', verbose_name="Sex")
    civil_status = models.CharField(max_length=30, choices=CIVIL_STATUS_CHOICES, default='Single', verbose_name="Civil Status")
    relationship_to_head = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, default='Head', verbose_name="Relationship to Household Head")

    educational_attainment = models.CharField(max_length=80, choices=EDUCATION_CHOICES, default='High School Graduate', verbose_name="Educational Attainment")
    occupation = models.CharField(max_length=120, blank=True, default="N/A", verbose_name="Occupation")
    employment_status = models.CharField(max_length=50, choices=EMPLOYMENT_CHOICES, default="Employed (Private)", verbose_name="Employment Status")
    contact_number = models.CharField(max_length=30, blank=True, default="", verbose_name="Contact Number")
    residency_status = models.CharField(max_length=40, choices=RESIDENCY_STATUS_CHOICES, default='Permanent Resident', verbose_name="Residency Status")

    # Demographic Classifications & Sectoral Tags
    is_pwd = models.BooleanField(default=False, verbose_name="PWD (Person with Disability)")
    is_4ps = models.BooleanField(default=False, verbose_name="4Ps Beneficiary")
    is_single_parent = models.BooleanField(default=False, verbose_name="Single / Solo Parent")
    is_voter = models.BooleanField(default=False, verbose_name="Registered Voter")
    voter_id = models.CharField(max_length=50, blank=True, default="", verbose_name="Voter ID No.")
    blood_type = models.CharField(max_length=10, blank=True, default="N/A", verbose_name="Blood Type")

    # Retained optional fields for backwards compatibility
    purok = models.CharField(max_length=150, blank=True, default="", verbose_name="Purok")
    household_number = models.CharField(max_length=50, blank=True, default="", verbose_name="Household No.")
    household_head = models.CharField(max_length=150, blank=True, default="", verbose_name="Head of Household")
    household_members_count = models.PositiveIntegerField(default=1, verbose_name="Household Members Count")
    gender = models.CharField(max_length=10, blank=True, default="", verbose_name="Gender")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resident_profile', verbose_name="User Account")

    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_updated = models.DateTimeField(auto_now=True, verbose_name="Date Updated")

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Resident"
        verbose_name_plural = "Residents"

    def save(self, *args, **kwargs):
        # Auto-compute full_name
        parts = [self.first_name.strip()]
        if self.middle_name and self.middle_name.strip():
            parts.append(self.middle_name.strip())
        parts.append(self.last_name.strip())
        self.full_name = " ".join(parts)

        # Sync gender and sex
        if not self.gender and self.sex:
            self.gender = self.sex
        elif not self.sex and self.gender:
            self.sex = self.gender

        # Sync household details if linked
        if self.household:
            self.household_number = self.household.household_number
            self.purok = self.household.purok
            self.household_head = self.household.head_name

        super().save(*args, **kwargs)

        # Auto-generate resident_id if not present
        if not self.resident_id:
            self.resident_id = f"RES-{self.id:04d}"
            Resident.objects.filter(id=self.id).update(resident_id=self.resident_id)

    def __str__(self):
        return f"{self.full_name} ({self.formatted_id})"

    @property
    def formatted_id(self):
        return self.resident_id or f"RES-{self.id:04d}"

    @property
    def is_minor(self):
        return self.age < 18

    @property
    def is_senior(self):
        return self.age >= 60

    @property
    def is_sk_youth(self):
        return 15 <= self.age <= 30

    @property
    def is_verified(self):
        if self.household:
            return self.household.is_verified
        return True


# ==========================================
# 4. OPTIONAL RESIDENT CONCERN (Secondary feature)
# ==========================================
class ResidentConcern(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]

    complainant_name = models.CharField(max_length=150, blank=True, default="", verbose_name="Complainant / Resident Name")
    contact_number = models.CharField(max_length=30, blank=True, default="", verbose_name="Contact Number")
    purok = models.CharField(max_length=100, blank=True, default="", verbose_name="Purok")
    subject = models.CharField(max_length=200, verbose_name="Subject / Title")
    category = models.CharField(max_length=100, default="General Concern", verbose_name="Category")
    description = models.TextField(verbose_name="Description / Details")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending', verbose_name="Status")
    admin_action_taken = models.TextField(blank=True, default="", verbose_name="Action Taken / Admin Notes")
    action_date = models.DateTimeField(null=True, blank=True, verbose_name="Action Date")
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="Date Submitted")

    # Backwards compatibility
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='concerns', verbose_name="Resident")
    admin_response = models.TextField(blank=True, default="", verbose_name="Admin Response")

    class Meta:
        ordering = ['-date_submitted']
        verbose_name = "Resident Concern"
        verbose_name_plural = "Resident Concerns"

    def __str__(self):
        return f"{self.subject} ({self.complainant_name}) [{self.status}]"

    @property
    def status_badge_class(self):
        mapping = {
            'Pending': 'warning text-dark',
            'Under Review': 'info text-dark',
            'In Progress': 'primary',
            'Resolved': 'success',
            'Rejected': 'danger',
        }
        return mapping.get(self.status, 'secondary')


# ==========================================
# 5. LEGACY / SECONDARY SERVICES (Retained for migration safety)
# ==========================================
class DocumentRequest(models.Model):
    DOCUMENT_TYPES = [
        ('Clearance', 'Barangay Clearance'),
        ('Indigency', 'Certificate of Indigency'),
        ('Residency', 'Certificate of Residency'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]
    or_number = models.CharField(max_length=50, blank=True, default="", verbose_name="O.R. Number")
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='documents', verbose_name="Resident")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, verbose_name="Document Type")
    purpose = models.CharField(max_length=200, verbose_name="Purpose")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Amount Paid")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Completed', verbose_name="Status")
    admin_notes = models.TextField(blank=True, default="", verbose_name="Admin Notes / Remarks")
    date_issued = models.DateTimeField(auto_now_add=True, verbose_name="Date Requested / Issued")

    class Meta:
        ordering = ['-date_issued']
        verbose_name = "Document Transaction"
        verbose_name_plural = "Document Transactions"


class BlotterCase(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Investigation'),
        ('Scheduled', 'Hearing Scheduled'),
        ('Settled', 'Settled (Amicable)'),
        ('Referred', 'Referred to Court'),
    ]
    case_number = models.CharField(max_length=50, unique=True, verbose_name="Case No.")
    complainant_name = models.CharField(max_length=150, verbose_name="Complainant")
    complainant_address = models.CharField(max_length=255, verbose_name="Complainant Address")
    respondent_name = models.CharField(max_length=150, verbose_name="Respondent")
    respondent_address = models.CharField(max_length=255, verbose_name="Respondent Address")
    incident_type = models.CharField(max_length=100, verbose_name="Incident Type")
    incident_location = models.CharField(max_length=255, blank=True, default="", verbose_name="Incident Location")
    details = models.TextField(blank=True, default="", verbose_name="Complaint Details")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending', verbose_name="Status")
    date_filed = models.DateTimeField(auto_now_add=True, verbose_name="Date Filed")

    class Meta:
        ordering = ['-date_filed']
        verbose_name = "Blotter Case"
        verbose_name_plural = "Blotter Cases"


class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Title")
    category = models.CharField(max_length=50, default="General", verbose_name="Category")
    content = models.TextField(verbose_name="Announcement Content")
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Posted By")
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name="Date Posted")

    class Meta:
        ordering = ['-date_posted']
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"


# ==========================================
# 6. SYSTEM AUDIT LOG (Activity Trail)
# ==========================================
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
        ('VERIFY', 'Verify Household'),
        ('PRINT', 'Print Document / ID'),
        ('LOGIN', 'User Login'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="User / Staff")
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Action Type")
    module_name = models.CharField(max_length=50, verbose_name="Module / Section")
    description = models.TextField(verbose_name="Description / Details")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {username} - {self.action_type} ({self.module_name})"

