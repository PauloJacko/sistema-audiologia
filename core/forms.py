from django import forms
from .models import Patient, Anamnesis, Audiogram, Threshold, SpeechAudiometry, LDL

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["rut", "first_name", "last_name", "birth_date", "sex", "phone", "email"]
        widgets = {
            "rut": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "birth_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

class AnamnesisForm(forms.ModelForm):
    class Meta:
        model = Anamnesis
        exclude = ["patient", "created_at"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "main_complaint": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "medication": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
            # Campos de texto simples
            "vertigo_type": forms.TextInput(attrs={"class": "form-control"}),
            "vertigo_duration": forms.TextInput(attrs={"class": "form-control"}),
            "vertigo_triggers": forms.TextInput(attrs={"class": "form-control"}),
            # Checkboxes
            "hearing_loss": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tinnitus": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "otalgia": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "otorrhea": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "vertigo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "noise_exposure": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "hearing_aids": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

class AudiogramForm(forms.ModelForm):
    class Meta:
        model = Audiogram
        fields = ["date", "exam_type", "transducer", "masking_used", "comments"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "exam_type": forms.Select(attrs={"class": "form-select"}),
            "transducer": forms.Select(attrs={"class": "form-select"}),
            "masking_used": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comments": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }

SYMBOL_CHOICES = [
    ("", "—"),
    ("O", "O (OD aérea s/m)"),
    ("X", "X (OI aérea s/m)"),
    ("[", "[ (OD ósea c/m)"),
    ("]", "] (OI ósea c/m)"),
    ("<", "< (OD ósea s/m)"),
    (">", "> (OI ósea s/m)"),
    ("Δ", "Delta (c/m genérico)"),
    ("◇", "Rombo / Campo libre"),
]


class ThresholdForm(forms.ModelForm):
    symbol = forms.ChoiceField(choices=SYMBOL_CHOICES, required=False)

    class Meta:
        model = Threshold
        fields = [
            "ear", "pathway", "symbol",
            "f_250", "f_500", "f_1000", "f_2000", "f_3000", "f_4000", "f_6000", "f_8000"
        ]
        widgets = {
            "ear": forms.Select(attrs={"class": "form-select"}),
            "pathway": forms.Select(attrs={"class": "form-select"}),
            "symbol": forms.Select(attrs={"class": "form-select"}),
            **{f"f_{f}": forms.NumberInput(attrs={"step": 1, "class": "form-control"}) for f in (250,500,1000,2000,3000,4000,6000,8000)}
        }

ThresholdFormSet = forms.modelformset_factory(
    Threshold,
    form=ThresholdForm,
    extra=0,
    can_delete=False
)


class SpeechForm(forms.ModelForm):
    class Meta:
        model = SpeechAudiometry
        exclude = ["patient"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "ear": forms.Select(attrs={"class": "form-select"}),
            "srt": forms.NumberInput(attrs={"class": "form-control"}),
            "wrs_percent": forms.NumberInput(attrs={"class": "form-control"}),
            "wrs_level_db": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.TextInput(attrs={"class": "form-control"}),
        }

class LDLForm(forms.ModelForm):
    class Meta:
        model = LDL
        exclude = ["patient"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "ear": forms.Select(attrs={"class": "form-select"}),
            "ldl_500": forms.NumberInput(attrs={"class": "form-control"}),
            "ldl_1k": forms.NumberInput(attrs={"class": "form-control"}),
            "ldl_2k": forms.NumberInput(attrs={"class": "form-control"}),
            "ldl_4k": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.TextInput(attrs={"class": "form-control"}),
        }
