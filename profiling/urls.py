from django.urls import path
from . import views

urlpatterns = [
    # Core Flow
    path('', views.landing_view, name='landing'),
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Household Profiling (Main Feature)
    path('households/', views.household_list_view, name='household_list'),
    path('households/masterlist/', views.household_list_view, name='households_masterlist'),
    path('households/add/', views.household_create_view, name='household_create'),
    path('households/<int:pk>/', views.household_detail_view, name='household_detail'),
    path('households/<int:pk>/edit/', views.household_edit_view, name='household_edit'),
    path('households/<int:pk>/delete/', views.household_delete_view, name='household_delete'),
    path('households/<int:pk>/submit-verification/', views.household_submit_verification_view, name='household_submit_verification'),

    # Admin Verification Workflow
    path('verification/', views.verification_queue_view, name='verification_queue'),
    path('verification/<int:pk>/action/', views.verification_action_view, name='verification_action'),

    # Resident Information (One Household -> Many Residents)
    path('residents/', views.resident_list_view, name='resident_list'),
    path('residents/add/', views.resident_create_view, name='resident_create'),
    path('residents/<int:pk>/', views.resident_detail_view, name='resident_detail'),
    path('residents/<int:pk>/edit/', views.resident_update_view, name='resident_update'),
    path('residents/<int:pk>/delete/', views.resident_delete_view, name='resident_delete'),
    path('residents/<int:pk>/id-card/', views.resident_id_card_view, name='resident_id_card'),

    # Reports & Data Export
    path('reports/', views.reports_view, name='reports'),
    path('reports/population/', views.reports_view, name='population_report'),
    path('reports/export/households/', views.export_households_csv_view, name='export_households_csv'),
    path('reports/export/residents/', views.export_residents_csv_view, name='export_residents_csv'),

    # Secondary: Resident Concerns
    path('concerns/', views.concerns_list_view, name='concerns_list'),
    path('concerns/add/', views.concern_create_view, name='concern_create'),
    path('concerns/<int:pk>/action/', views.concern_action_view, name='concern_action'),
    path('concerns/admin/', views.concerns_list_view, name='admin_concerns'),

    # Administration: User Management, Profile, & Audit Logs
    path('users/', views.user_management_view, name='user_management'),
    path('users/<int:pk>/toggle/', views.user_toggle_status_view, name='user_toggle_status'),
    path('profile/', views.admin_profile_view, name='admin_profile'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),

    # Secondary / Legacy Service Endpoints
    path('documents/', views.document_issuance_view, name='document_issuance'),
    path('blotter/', views.blotter_records_view, name='blotter_records'),
]
