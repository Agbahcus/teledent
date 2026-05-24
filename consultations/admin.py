from django.contrib import admin
from .models import Consultation, ConsultationImage, ResponseTemplate

class ConsultationImageInline(admin.TabularInline):
    model = ConsultationImage
    extra = 0
    readonly_fields = ('uploaded_at',)

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'status', 'urgency', 'created_at', 'dentist')
    list_filter = ('status', 'urgency', 'created_at')
    search_fields = ('patient_name', 'patient_email', 'patient_phone')
    inlines = [ConsultationImageInline]
    readonly_fields = ('id', 'created_at', 'urgency', 'triage_summary')
    
    fieldsets = (
        ('Patient Info', {'fields': ('id', 'patient_name', 'patient_phone', 'patient_email', 'patient_complaint')}),
        ('Triage Details', {'fields': ('pain_level', 'symptom_duration', 'urgency', 'triage_summary')}),
        ('Medical Flags', {'fields': ('has_swelling', 'has_bleeding', 'has_fever', 'has_trauma')}),
        ('Status & Response', {'fields': ('status', 'dentist', 'dentist_diagnosis', 'dentist_treatment_plan', 'dentist_medications')}),
    )

@admin.register(ResponseTemplate)
class ResponseTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'dentist')
    search_fields = ('title', 'diagnosis')
