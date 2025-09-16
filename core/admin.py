from django.contrib import admin
from .models import Patient, Anamnesis, Audiogram, Threshold, SpeechAudiometry, LDL

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("rut", "last_name", "first_name", "birth_date", "sex")
    search_fields = ("rut", "first_name", "last_name", "email")

class ThresholdInline(admin.TabularInline):
    model = Threshold
    extra = 0

@admin.register(Audiogram)
class AudiogramAdmin(admin.ModelAdmin):
    list_display = ("patient", "date", "exam_type", "transducer", "masking_used")
    inlines = [ThresholdInline]

admin.site.register(Anamnesis)
admin.site.register(SpeechAudiometry)
admin.site.register(LDL)
