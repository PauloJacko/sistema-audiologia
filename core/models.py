from __future__ import annotations
from django.db import models
from django.utils import timezone
from datetime import date
from typing import Optional

SEX_CHOICES = (
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("O", "Otro / Prefiere no decir"),
)

EAR_CHOICES = (
    ("R", "Oído Derecho"),
    ("L", "Oído Izquierdo"),
    ("B", "Binaural / Campo libre"),
)

PATHWAY_CHOICES = (
    ("AC", "Aérea"),
    ("BC", "Ósea"),
)

AUDIOMETRY_TYPE_CHOICES = (
    ("TONAL", "Tonal (Aérea/Ósea)"),
    ("FIELD", "Campo Libre"),
    ("PLAY", "Audiometría Infantil/Play"),
    ("HF", "Alta Frecuencia"),
)

TRANSDUCER_CHOICES = (
    ("SUPRA", "Supraaural"),
    ("CIRCUM", "Circumaural"),
    ("INSERT", "Insert"),
    ("SPEAKER", "Parlante"),
)

FREQS = [250, 500, 1000, 2000, 3000, 4000, 6000, 8000]

class Patient(models.Model):
    rut = models.CharField("RUT", max_length=20, unique=True)
    first_name = models.CharField("Nombres", max_length=80)
    last_name = models.CharField("Apellidos", max_length=80)
    birth_date = models.DateField("Fecha de nacimiento", null=True, blank=True)
    sex = models.CharField("Sexo", max_length=1, choices=SEX_CHOICES, blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    email = models.EmailField("Email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name}, {self.first_name} — {self.rut}"

    def age_on(self, on_date: date | None = None) -> int | None:
        if not self.birth_date:
            return None
        d = on_date or date.today()
        return d.year - self.birth_date.year - ((d.month, d.day) < (self.birth_date.month, self.birth_date.day))


class Anamnesis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="anamneses")
    date = models.DateField(default=timezone.now)
    # Motivo y antecedentes
    main_complaint = models.TextField("Motivo de consulta", blank=True)
    hearing_loss = models.BooleanField("Hipoacusia", default=False)
    tinnitus = models.BooleanField("Acúfenos / Tinnitus", default=False)
    otalgia = models.BooleanField("Otalgia", default=False)
    otorrhea = models.BooleanField("Otorrhea", default=False)
    vertigo = models.BooleanField("Vértigo", default=False)
    noise_exposure = models.BooleanField("Exposición a ruido", default=False)
    hearing_aids = models.BooleanField("Uso de audífonos", default=False)
    medication = models.TextField("Medicamentos / Ototóxicos", blank=True)

    # Vértigo (básico)
    vertigo_type = models.CharField("Tipo de vértigo (si aplica)", max_length=120, blank=True)
    vertigo_duration = models.CharField("Duración de crisis", max_length=120, blank=True)
    vertigo_triggers = models.CharField("Desencadenantes", max_length=200, blank=True)

    notes = models.TextField("Notas", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]


class Audiogram(models.Model):
    """Cabecera del examen (tipo, transductor, etc.). PTA se calcula desde Thresholds."""
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name="audiograms")
    date = models.DateField(default=timezone.now)
    exam_type = models.CharField(max_length=10, choices=AUDIOMETRY_TYPE_CHOICES, default="TONAL")
    transducer = models.CharField(max_length=10, choices=TRANSDUCER_CHOICES, default="INSERT")
    masking_used = models.BooleanField("Se usó enmascaramiento", default=False)
    comments = models.TextField("Comentarios", blank=True)

    class Meta:
        ordering = ["-date", "-id"]

    # --- PTA por edad: Adulto = (500, 1000, 2000); Pediátrico = (1000, 2000, 4000)
    def pta(self, ear: str, on_date: Optional[date] = None) -> Optional[float]:
        if ear not in ("R", "L", "B"):
            return None

        # Determinar esquema por edad
        age = self.patient.age_on(self.date)
        pediatric = (age is not None and age < 15)  # regla simple
        triple = (1000, 2000, 4000) if pediatric else (500, 1000, 2000)

        # Buscar thresholds AÉREA del oído indicado (o binaural)
        qs = self.thresholds.filter(ear=ear, pathway="AC").first()
        if not qs:
            return None

        values = [getattr(qs, "f_{}".format(fq), None) for fq in triple]
        vals = [v for v in values if isinstance(v, (int, float))]
        if len(vals) < 3:
            return None

        return round(sum(vals) / 3.0, 1)

    @property
    def pta_right(self) -> Optional[float]:
        return self.pta("R")

    @property
    def pta_left(self) -> Optional[float]:
        return self.pta("L")

    @property
    def pta_binaural(self) -> Optional[float]:
        return self.pta("B")


class Threshold(models.Model):
    """Umbrales por oído y vía. Incluye símbolo para el gráfico (opcional)."""
    audiogram = models.ForeignKey(Audiogram, on_delete=models.CASCADE, related_name="thresholds")
    ear = models.CharField(max_length=1, choices=EAR_CHOICES)
    pathway = models.CharField(max_length=2, choices=PATHWAY_CHOICES, default="AC")

    # Simbología (opcional; referencial para graficar)
    # Ejemplos: "O" (OD aérea sin máscara), "X" (OI aérea sin máscara),
    # "<" (OD ósea sin máscara), ">" (OI ósea sin máscara), "[", "]" con máscara, etc.
    symbol = models.CharField("Símbolo", max_length=2, blank=True)

    # Umbrales por frecuencia (dB HL)
    f_250  = models.IntegerField(null=True, blank=True)
    f_500  = models.IntegerField(null=True, blank=True)
    f_1000 = models.IntegerField(null=True, blank=True)
    f_2000 = models.IntegerField(null=True, blank=True)
    f_3000 = models.IntegerField(null=True, blank=True)
    f_4000 = models.IntegerField(null=True, blank=True)
    f_6000 = models.IntegerField(null=True, blank=True)
    f_8000 = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("audiogram", "ear", "pathway")


class SpeechAudiometry(models.Model):
    """Audiometría vocal: SRT/SDT y comprensión de la palabra (WRS)."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="speech_tests")
    date = models.DateField(default=timezone.now)
    ear = models.CharField(max_length=1, choices=EAR_CHOICES, default="R")
    srt = models.IntegerField("SRT/SDT (dB HL)", null=True, blank=True)
    wrs_percent = models.IntegerField("Reconocimiento de Palabras (%)", null=True, blank=True)
    wrs_level_db = models.IntegerField("Nivel de presentación (dB HL)", null=True, blank=True)
    notes = models.CharField("Notas", max_length=200, blank=True)

    class Meta:
        ordering = ["-date", "-id"]


class LDL(models.Model):
    """Límites de disconfort (dB HL)."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="ldl_tests")
    date = models.DateField(default=timezone.now)
    ear = models.CharField(max_length=1, choices=EAR_CHOICES, default="R")
    ldl_500 = models.IntegerField(null=True, blank=True)
    ldl_1k = models.IntegerField(null=True, blank=True)
    ldl_2k = models.IntegerField(null=True, blank=True)
    ldl_4k = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date", "-id"]
