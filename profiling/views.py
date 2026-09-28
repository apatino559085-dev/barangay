import csv
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .models import (
    Household, Resident, ResidentConcern, UserProfile,
    DocumentRequest, BlotterCase, Announcement,
    PUROK_CHOICES, HOUSE_TYPE_CHOICES, HOUSING_OWNERSHIP_CHOICES,
    WATER_SOURCE_CHOICES, ELECTRICITY_CHOICES, TOILET_FACILITY_CHOICES,
    CIVIL_STATUS_CHOICES, RELATIONSHIP_CHOICES, EDUCATION_CHOICES,
    EMPLOYMENT_CHOICES, RESIDENCY_STATUS_CHOICES
)
from .forms import (
    HouseholdForm, ResidentForm, HouseholdVerificationForm,
    ResidentConcernForm, UserCreateForm
)


# ==========================================
# AUTHENTICATION & ROLE HELPERS
# ==========================================
def is_admin(user):
    if not user.is_authenticated:
        return False
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'Admin')

def is_authorized_user(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or is_admin(user)

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not is_admin(request.user):
            messages.error(request, "Access denied. Only Barangay Administrators have permission to access that feature.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# 1. PUBLIC LANDING & AUTHENTICATION
# ==========================================
def landing_view(request):
    """Barangay Profiling System public landing overview."""
    total_residents = Resident.objects.count()
    total_households = Household.objects.count()
    verified_households = Household.objects.filter(verification_status='Approved').count()
    return render(request, 'profiling/landing.html', {
        'total_residents': total_residents,
        'total_households': total_households,
        'verified_households': verified_households,
    })


def admin_login_view(request):
    """Official Login Page for Barangay Admin and Staff."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            role_title = "Barangay Administrator" if is_admin(user) else "Barangay Staff"
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}! Logged in as {role_title}.")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm(request)

    return render(request, 'profiling/login.html', {'form': form})


@login_required
def admin_logout_view(request):
    """Logs out official and clears session."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('admin_login')


# ==========================================
# 2. DASHBOARD VIEW
# ==========================================
@login_required
def dashboard_view(request):
    """Executive dashboard with summary statistics and easy-to-understand cards & tables."""
    total_households = Household.objects.count()
    total_residents = Resident.objects.count()
    male_residents = Resident.objects.filter(sex='Male').count()
    female_residents = Resident.objects.filter(sex='Female').count()

    pending_profiles = Household.objects.filter(verification_status='Pending Verification').count()
    verified_profiles = Household.objects.filter(verification_status='Approved').count()
    draft_profiles = Household.objects.filter(verification_status='Draft').count()
    returned_profiles = Household.objects.filter(verification_status='Returned for Correction').count()

    # Households and Residents per Purok breakdown
    purok_data = []
    for purok_code, purok_label in PUROK_CHOICES:
        hh_count = Household.objects.filter(purok=purok_code).count()
        res_count = Resident.objects.filter(Q(household__purok=purok_code) | Q(purok=purok_code)).count()
        verified_count = Household.objects.filter(purok=purok_code, verification_status='Approved').count()
        if hh_count > 0 or res_count > 0:
            purok_data.append({
                'purok': purok_label,
                'households': hh_count,
                'residents': res_count,
                'verified': verified_count,
            })

    # Recent household activity
    recent_households = Household.objects.all().order_by('-date_updated')[:8]

    # Recent concerns count
    pending_concerns = ResidentConcern.objects.filter(status='Pending').count()

    context = {
        'total_households': total_households,
        'total_residents': total_residents,
        'male_residents': male_residents,
        'female_residents': female_residents,
        'pending_profiles': pending_profiles,
        'verified_profiles': verified_profiles,
        'draft_profiles': draft_profiles,
        'returned_profiles': returned_profiles,
        'purok_data': purok_data,
        'recent_households': recent_households,
        'pending_concerns': pending_concerns,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/dashboard.html', context)


# ==========================================
# 3. HOUSEHOLD PROFILING (Core System Feature)
# ==========================================
@login_required
def household_list_view(request):
    """Household Masterlist with search, filtering, and quick actions."""
    query = request.GET.get('q', '').strip()
    purok_filter = request.GET.get('purok', '').strip()
    status_filter = request.GET.get('status', '').strip()
    verification_filter = request.GET.get('verification', '').strip()

    households = Household.objects.all().prefetch_related('residents')

    if query:
        households = households.filter(
            Q(household_number__icontains=query) |
            Q(head_name__icontains=query) |
            Q(complete_address__icontains=query) |
            Q(purok__icontains=query)
        )

    if purok_filter:
        households = households.filter(purok=purok_filter)

    if status_filter:
        households = households.filter(household_status=status_filter)

    if verification_filter:
        households = households.filter(verification_status=verification_filter)

    paginator = Paginator(households, 12)
    page = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    context = {
        'page_obj': page_obj,
        'purok_choices': PUROK_CHOICES,
        'verification_choices': ['Draft', 'Pending Verification', 'Approved', 'Returned for Correction'],
        'query': query,
        'purok_filter': purok_filter,
        'status_filter': status_filter,
        'verification_filter': verification_filter,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/household_list.html', context)


@login_required
def household_create_view(request):
    """Barangay Staff collects and profiles a household."""
    if request.method == 'POST':
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save(commit=False)
            household.profiled_by = request.user
            household.verification_status = 'Draft'
            household.save()
            messages.success(
                request,
                f"Household #{household.household_number} successfully registered as Draft! "
                "Now please add the residents belonging to this household below."
            )
            return redirect('household_detail', pk=household.pk)
        else:
            messages.error(request, "Please correct the highlighted errors in the form.")
    else:
        # Pre-fill next household number suggestion
        next_count = Household.objects.count() + 1
        initial_number = f"HH-{timezone.now().year}-{next_count:03d}"
        form = HouseholdForm(initial={'household_number': initial_number})

    context = {
        'form': form,
        'title': 'New Household Profile',
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/household_form.html', context)


@login_required
def household_detail_view(request, pk):
    """Household profile view showing amenities, members, verification status, and admin review."""
    household = get_object_or_404(Household.objects.prefetch_related('residents'), pk=pk)
    residents = household.residents.all().order_by('relationship_to_head', 'age')

    # Verification form for Admins
    verification_form = None
    if is_admin(request.user):
        verification_form = HouseholdVerificationForm(instance=household)

    # Resident form for quick add within household
    resident_form = ResidentForm()

    context = {
        'household': household,
        'residents': residents,
        'verification_form': verification_form,
        'resident_form': resident_form,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/household_detail.html', context)


@login_required
def household_edit_view(request, pk):
    """Edit household details."""
    household = get_object_or_404(Household, pk=pk)

    # If user is staff, only draft or returned profiles may be edited
    if not is_admin(request.user) and household.verification_status == 'Approved':
        messages.warning(request, "This household is already verified and approved. Only administrators can edit approved records.")
        return redirect('household_detail', pk=household.pk)

    if request.method == 'POST':
        form = HouseholdForm(request.POST, instance=household)
        if form.is_valid():
            hh = form.save()
            # If was returned for correction and edited by staff, keep track
            messages.success(request, f"Household #{hh.household_number} profile updated successfully!")
            return redirect('household_detail', pk=hh.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = HouseholdForm(instance=household)

    context = {
        'form': form,
        'household': household,
        'title': f'Edit Household Profile: {household.household_number}',
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/household_form.html', context)


@login_required
def household_delete_view(request, pk):
    """Delete household profile (Admin only)."""
    household = get_object_or_404(Household, pk=pk)
    if not is_admin(request.user):
        messages.error(request, "Only Barangay Administrators can delete household profiles.")
        return redirect('household_detail', pk=household.pk)

    if request.method == 'POST':
        hh_num = household.household_number
        household.delete()
        messages.success(request, f"Household #{hh_num} and its resident records have been deleted.")
        return redirect('household_list')

    return render(request, 'profiling/household_confirm_delete.html', {'household': household})


@login_required
def household_submit_verification_view(request, pk):
    """Staff submits household profile for admin verification."""
    household = get_object_or_404(Household, pk=pk)

    if household.verification_status == 'Approved':
        messages.info(request, "This household is already verified and approved.")
        return redirect('household_detail', pk=pk)

    if household.residents.count() == 0:
        messages.warning(request, "Cannot submit an empty household. Please add at least one resident member before submitting.")
        return redirect('household_detail', pk=pk)

    household.verification_status = 'Pending Verification'
    household.save()
    messages.success(
        request,
        f"Household #{household.household_number} has been submitted for Admin Verification. "
        "The barangay administrator will review and approve the profile."
    )
    return redirect('household_detail', pk=pk)


# ==========================================
# 4. PROFILE VERIFICATION (Admin Workflow)
# ==========================================
@login_required
@admin_required
def verification_queue_view(request):
    """Admin queue of household profiles waiting for verification review."""
    tab = request.GET.get('tab', 'pending')

    if tab == 'approved':
        profiles = Household.objects.filter(verification_status='Approved')
    elif tab == 'returned':
        profiles = Household.objects.filter(verification_status='Returned for Correction')
    elif tab == 'draft':
        profiles = Household.objects.filter(verification_status='Draft')
    else:
        tab = 'pending'
        profiles = Household.objects.filter(verification_status='Pending Verification')

    profiles = profiles.prefetch_related('residents').order_by('-date_updated')

    counts = {
        'pending': Household.objects.filter(verification_status='Pending Verification').count(),
        'approved': Household.objects.filter(verification_status='Approved').count(),
        'returned': Household.objects.filter(verification_status='Returned for Correction').count(),
        'draft': Household.objects.filter(verification_status='Draft').count(),
    }

    paginator = Paginator(profiles, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'tab': tab,
        'counts': counts,
    }
    return render(request, 'profiling/verification_queue.html', context)


@login_required
@admin_required
def verification_action_view(request, pk):
    """Admin approves or returns a household profile with remarks."""
    household = get_object_or_404(Household, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_remarks = request.POST.get('admin_remarks', '').strip()

        if action == 'Approve':
            household.verification_status = 'Approved'
            household.verified_by = request.user
            household.date_verified = timezone.now()
            if admin_remarks:
                household.admin_remarks = admin_remarks
            household.save()
            messages.success(request, f"Household #{household.household_number} profile has been APPROVED and is now a verified barangay record.")
        elif action == 'Return':
            household.verification_status = 'Returned for Correction'
            household.admin_remarks = admin_remarks or "Please review and correct the submitted information."
            household.save()
            messages.warning(request, f"Household #{household.household_number} has been RETURNED for correction with your notes.")
        else:
            messages.error(request, "Invalid verification action.")

    return redirect('household_detail', pk=pk)


# ==========================================
# 5. RESIDENT INFORMATION (One Household -> Many Residents)
# ==========================================
@login_required
def resident_list_view(request):
    """Resident Masterlist with search by Name, Household No., Purok, and multifaceted filtering."""
    query = request.GET.get('q', '').strip()
    purok_filter = request.GET.get('purok', '').strip()
    sex_filter = request.GET.get('sex', '').strip()
    civil_filter = request.GET.get('civil_status', '').strip()
    age_group = request.GET.get('age_group', '').strip()
    verification_filter = request.GET.get('verification', '').strip()

    residents = Resident.objects.all().select_related('household')

    if query:
        residents = residents.filter(
            Q(full_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(resident_id__icontains=query) |
            Q(household__household_number__icontains=query) |
            Q(household_number__icontains=query) |
            Q(purok__icontains=query) |
            Q(household__purok__icontains=query)
        )

    if purok_filter:
        residents = residents.filter(Q(household__purok=purok_filter) | Q(purok=purok_filter))

    if sex_filter:
        residents = residents.filter(sex=sex_filter)

    if civil_filter:
        residents = residents.filter(civil_status=civil_filter)

    if age_group == 'children':
        residents = residents.filter(age__lte=14)
    elif age_group == 'youth':
        residents = residents.filter(age__gte=15, age__lte=24)
    elif age_group == 'adults':
        residents = residents.filter(age__gte=25, age__lte=59)
    elif age_group == 'seniors':
        residents = residents.filter(age__gte=60)

    if verification_filter:
        if verification_filter == 'Approved':
            residents = residents.filter(household__verification_status='Approved')
        elif verification_filter == 'Pending':
            residents = residents.filter(household__verification_status='Pending Verification')
        elif verification_filter == 'Draft':
            residents = residents.filter(household__verification_status='Draft')

    paginator = Paginator(residents, 15)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'purok_choices': PUROK_CHOICES,
        'civil_choices': CIVIL_STATUS_CHOICES,
        'query': query,
        'purok_filter': purok_filter,
        'sex_filter': sex_filter,
        'civil_filter': civil_filter,
        'age_group': age_group,
        'verification_filter': verification_filter,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/resident_list.html', context)


@login_required
def resident_create_view(request):
    """Add a resident to a household."""
    household_id = request.GET.get('household') or request.POST.get('household_id')
    selected_household = None
    if household_id:
        selected_household = get_object_or_404(Household, pk=household_id)

    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident = form.save(commit=False)
            if selected_household:
                resident.household = selected_household
            elif resident.household:
                selected_household = resident.household
            elif request.POST.get('household_id'):
                hh_from_id = Household.objects.filter(pk=request.POST.get('household_id')).first()
                if hh_from_id:
                    resident.household = hh_from_id
                    selected_household = hh_from_id

            if resident.household:
                resident.household_number = resident.household.household_number
                resident.purok = resident.household.purok
                resident.household_head = resident.household.head_name

            resident.save()

            # Update household member count if greater
            if selected_household:
                actual_count = selected_household.residents.count()
                if actual_count > selected_household.members_count:
                    selected_household.members_count = actual_count
                    selected_household.save()

            messages.success(request, f"Resident '{resident.full_name}' ({resident.formatted_id}) successfully added!")
            if selected_household:
                return redirect('household_detail', pk=selected_household.pk)
            return redirect('resident_list')
        else:
            messages.error(request, "Please correct the errors in the resident form.")
    else:
        form = ResidentForm()

    context = {
        'form': form,
        'selected_household': selected_household,
        'households': Household.objects.all().order_by('household_number') if not selected_household else None,
        'title': f'Add Resident Member' + (f' for {selected_household.household_number}' if selected_household else ''),
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/resident_form.html', context)


@login_required
def resident_detail_view(request, pk):
    """Resident Profile sheet."""
    resident = get_object_or_404(Resident.objects.select_related('household'), pk=pk)
    context = {
        'resident': resident,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/resident_detail.html', context)


@login_required
def resident_update_view(request, pk):
    """Edit resident record."""
    resident = get_object_or_404(Resident, pk=pk)

    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            r = form.save()
            messages.success(request, f"Resident '{r.full_name}' record updated successfully!")
            if r.household:
                return redirect('household_detail', pk=r.household.pk)
            return redirect('resident_detail', pk=r.pk)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ResidentForm(instance=resident)

    context = {
        'form': form,
        'resident': resident,
        'title': f'Edit Resident: {resident.full_name}',
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/resident_form.html', context)


@login_required
def resident_delete_view(request, pk):
    """Delete resident record (Admin only)."""
    resident = get_object_or_404(Resident, pk=pk)
    if not is_admin(request.user):
        messages.error(request, "Only Barangay Administrators have permission to delete resident records.")
        return redirect('resident_detail', pk=resident.pk)

    household_pk = resident.household.pk if resident.household else None

    if request.method == 'POST':
        name = resident.full_name
        resident.delete()
        messages.success(request, f"Resident '{name}' has been removed.")
        if household_pk:
            return redirect('household_detail', pk=household_pk)
        return redirect('resident_list')

    return render(request, 'profiling/resident_confirm_delete.html', {'resident': resident})


# ==========================================
# 6. REPORTS & ANALYTICS
# ==========================================
@login_required
def reports_view(request):
    """
    Comprehensive Barangay Profiling Reports:
    - Household Masterlist summary
    - Resident Masterlist summary
    - Population by Purok
    - Male and Female Population
    - Age Group Distribution
    - Number of Residents per Household
    - Household Summary (ownership, house type, water, electricity, sanitation)
    """
    total_households = Household.objects.count()
    verified_households = Household.objects.filter(verification_status='Approved').count()
    total_residents = Resident.objects.count()

    # Gender breakdown
    male_count = Resident.objects.filter(sex='Male').count()
    female_count = Resident.objects.filter(sex='Female').count()
    male_pct = round((male_count / total_residents * 100), 1) if total_residents else 0
    female_pct = round((female_count / total_residents * 100), 1) if total_residents else 0

    # Age groups
    children_count = Resident.objects.filter(age__lte=14).count()
    youth_count = Resident.objects.filter(age__gte=15, age__lte=24).count()
    adults_count = Resident.objects.filter(age__gte=25, age__lte=59).count()
    seniors_count = Resident.objects.filter(age__gte=60).count()

    # Population & Households by Purok
    purok_breakdown = []
    for code, label in PUROK_CHOICES:
        hh = Household.objects.filter(purok=code).count()
        res = Resident.objects.filter(Q(household__purok=code) | Q(purok=code)).count()
        males = Resident.objects.filter(Q(household__purok=code) | Q(purok=code), sex='Male').count()
        females = Resident.objects.filter(Q(household__purok=code) | Q(purok=code), sex='Female').count()
        if hh > 0 or res > 0:
            purok_breakdown.append({
                'purok': label,
                'households': hh,
                'residents': res,
                'males': males,
                'females': females,
                'percent': round((res / total_residents * 100), 1) if total_residents else 0
            })

    # Household Summary by Characteristics
    ownership_stats = Household.objects.values('housing_ownership').annotate(count=Count('id')).order_by('-count')
    house_type_stats = Household.objects.values('house_type').annotate(count=Count('id')).order_by('-count')
    water_stats = Household.objects.values('water_source').annotate(count=Count('id')).order_by('-count')
    electricity_stats = Household.objects.values('electricity').annotate(count=Count('id')).order_by('-count')
    toilet_stats = Household.objects.values('toilet_facility').annotate(count=Count('id')).order_by('-count')

    # Household size distribution
    small_hh = Household.objects.filter(members_count__lte=3).count()
    medium_hh = Household.objects.filter(members_count__gte=4, members_count__lte=6).count()
    large_hh = Household.objects.filter(members_count__gte=7).count()

    context = {
        'total_households': total_households,
        'verified_households': verified_households,
        'total_residents': total_residents,
        'male_count': male_count,
        'female_count': female_count,
        'male_pct': male_pct,
        'female_pct': female_pct,
        'children_count': children_count,
        'youth_count': youth_count,
        'adults_count': adults_count,
        'seniors_count': seniors_count,
        'purok_breakdown': purok_breakdown,
        'ownership_stats': ownership_stats,
        'house_type_stats': house_type_stats,
        'water_stats': water_stats,
        'electricity_stats': electricity_stats,
        'toilet_stats': toilet_stats,
        'small_hh': small_hh,
        'medium_hh': medium_hh,
        'large_hh': large_hh,
        'today': timezone.now().strftime('%B %d, %Y'),
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/reports.html', context)


@login_required
def export_households_csv_view(request):
    """Export Household Masterlist to CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Barangay_Households_{timezone.now().strftime("%Y%m%d")}.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Household No.', 'Purok', 'Address', 'Head of Family', 'Contact No.',
        'Members Count', 'House Type', 'Ownership', 'Water Source', 'Electricity',
        'Toilet Facility', 'Status', 'Verification Status', 'Date Profiled'
    ])
    for h in Household.objects.all().order_by('household_number'):
        writer.writerow([
            h.household_number, h.purok, h.complete_address, h.head_name, h.contact_number,
            h.members_count, h.house_type, h.housing_ownership, h.water_source,
            h.electricity, h.toilet_facility, h.household_status, h.verification_status,
            h.date_profiled.strftime('%Y-%m-%d')
        ])
    return response


@login_required
def export_residents_csv_view(request):
    """Export Resident Masterlist to CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Barangay_Residents_{timezone.now().strftime("%Y%m%d")}.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Resident ID', 'Full Name', 'Age', 'Sex', 'Civil Status', 'Household No.',
        'Purok', 'Relationship to Head', 'Educational Attainment', 'Occupation',
        'Employment Status', 'Contact No.', 'Residency Status', 'Profile Status'
    ])
    for r in Resident.objects.all().select_related('household').order_by('last_name', 'first_name'):
        h_no = r.household.household_number if r.household else r.household_number
        purok = r.household.purok if r.household else r.purok
        v_status = r.household.verification_status if r.household else 'N/A'
        writer.writerow([
            r.formatted_id, r.full_name, r.age, r.sex, r.civil_status, h_no,
            purok, r.relationship_to_head, r.educational_attainment, r.occupation,
            r.employment_status, r.contact_number, r.residency_status, v_status
        ])
    return response


# ==========================================
# 7. RESIDENT CONCERNS (Secondary Feature)
# ==========================================
@login_required
def concerns_list_view(request):
    """List of submitted resident concerns (secondary feature)."""
    status_filter = request.GET.get('status', '').strip()
    concerns = ResidentConcern.objects.all()
    if status_filter:
        concerns = concerns.filter(status=status_filter)

    paginator = Paginator(concerns, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    form = ResidentConcernForm()

    context = {
        'page_obj': page_obj,
        'form': form,
        'status_filter': status_filter,
        'statuses': ['Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected'],
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/concerns_list.html', context)


@login_required
def concern_create_view(request):
    """File a resident concern."""
    if request.method == 'POST':
        form = ResidentConcernForm(request.POST)
        if form.is_valid():
            concern = form.save(commit=False)
            concern.status = 'Pending'
            concern.save()
            messages.success(request, f"Concern '{concern.subject}' recorded successfully!")
        else:
            messages.error(request, "Failed to submit concern. Please check the inputs.")
    return redirect('concerns_list')


@login_required
def concern_action_view(request, pk):
    """Update concern status and action taken (Admin or Staff)."""
    concern = get_object_or_404(ResidentConcern, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        action_notes = request.POST.get('action_notes', '').strip()
        if new_status:
            concern.status = new_status
            if action_notes:
                concern.admin_action_taken = action_notes
                concern.admin_response = action_notes
            concern.action_date = timezone.now()
            concern.save()
            messages.success(request, f"Concern updated to '{new_status}'.")
    return redirect('concerns_list')


# ==========================================
# 8. USER MANAGEMENT (Admin Only)
# ==========================================
@login_required
@admin_required
def user_management_view(request):
    """Admin page to view and manage authorized barangay users."""
    users = User.objects.all().select_related('profile').order_by('-is_superuser', 'username')
    form = UserCreateForm()

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User '{user.username}' created successfully!")
            return redirect('user_management')
        else:
            messages.error(request, "Please check the errors in the user creation form.")

    context = {
        'users': users,
        'form': form,
        'is_admin': True,
    }
    return render(request, 'profiling/user_management.html', context)


@login_required
@admin_required
def user_toggle_status_view(request, pk):
    """Activate or deactivate user account."""
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
        return redirect('user_management')

    target_user.is_active = not target_user.is_active
    target_user.save()
    status_label = "activated" if target_user.is_active else "deactivated"
    messages.info(request, f"User account '{target_user.username}' has been {status_label}.")
    return redirect('user_management')


# ==========================================
# 9. ADMIN PROFILE & SECONDARY ISSUANCES
# ==========================================
@login_required
def admin_profile_view(request):
    """Admin / Staff user profile settings."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()

            profile.full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            profile.contact_number = request.POST.get('contact_number', '')
            profile.designation = request.POST.get('designation', '')
            profile.save()

            messages.success(request, "Your profile information has been updated.")
            return redirect('admin_profile')

        elif 'change_password' in request.POST:
            pass_form = PasswordChangeForm(request.user, request.POST)
            if pass_form.is_valid():
                user = pass_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully!")
                return redirect('admin_profile')
            else:
                messages.error(request, "Password change failed. Please verify your old password and requirements.")

    pass_form = PasswordChangeForm(request.user)
    context = {
        'profile': profile,
        'pass_form': pass_form,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'profiling/admin_profile.html', context)


# Legacy views retained so existing links/templates don't break
@login_required
def document_issuance_view(request):
    documents = DocumentRequest.objects.all().select_related('resident')[:20]
    return render(request, 'profiling/document_issuance.html', {'documents': documents})

@login_required
def blotter_records_view(request):
    blotters = BlotterCase.objects.all()[:20]
    return render(request, 'profiling/blotter_records.html', {'blotters': blotters})
