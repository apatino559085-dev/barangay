from django.contrib import admin
from .models import Resident


@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'household_number', 'relationship_to_head', 'age', 'gender', 'civil_status', 'purok', 'date_created')
    list_filter = ('gender', 'civil_status', 'relationship_to_head', 'purok')
    search_fields = ('full_name', 'purok', 'occupation', 'household_number', 'household_head')
    ordering = ('-date_created',)
