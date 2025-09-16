from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory

from .models import Patient, Anamnesis, Audiogram, Threshold, SpeechAudiometry, LDL
from .forms import (
    PatientForm, AnamnesisForm, AudiogramForm, ThresholdForm, ThresholdFormSet,
    SpeechForm, LDLForm
)

@login_required
def home(request):
    # Dashboard simple: últimos pacientes y acciones rápidas
    patients = Patient.objects.order_by("-id")[:8]
    return render(request, "core/home.html", {"patients": patients})

# --------- Pacientes ---------
@login_required
def patient_list(request):
    q = request.GET.get("q", "").strip()
    qs = Patient.objects.all()
    if q:
        qs = qs.filter(last_name__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(rut__icontains=q)
    qs = qs.order_by("last_name", "first_name")
    return render(request, "core/patient_list.html", {"patients": qs, "q": q})

@login_required
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            p = form.save()
            messages.success(request, "Paciente creado correctamente.")
            return redirect("patient_detail", pk=p.pk)
    else:
        form = PatientForm()
    return render(request, "core/patient_form.html", {"form": form, "title": "Nuevo Paciente"})

@login_required
def patient_detail(request, pk):
    p = get_object_or_404(Patient, pk=pk)
    anamneses = p.anamneses.all()[:5]
    audiograms = p.audiograms.all()[:5]
    speech = p.speech_tests.all()[:5]
    ldl = p.ldl_tests.all()[:5]
    return render(request, "core/patient_detail.html", {
        "patient": p,
        "anamneses": anamneses,
        "audiograms": audiograms,
        "speech": speech,
        "ldl": ldl,
    })

# --------- Anamnesis ---------
@login_required
def anamnesis_create(request, patient_pk):
    p = get_object_or_404(Patient, pk=patient_pk)
    if request.method == "POST":
        form = AnamnesisForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.patient = p
            a.save()
            messages.success(request, "Anamnesis guardada.")
            return redirect("patient_detail", pk=p.pk)
    else:
        form = AnamnesisForm()
    return render(request, "core/anamnesis_form.html", {"form": form, "patient": p})

# --------- Audiometría ---------
@login_required
def audiogram_create(request, patient_pk):
    p = get_object_or_404(Patient, pk=patient_pk)
    ThresholdFS = modelformset_factory(Threshold, form=ThresholdForm, extra=0, can_delete=False)

    if request.method == "POST":
        a_form = AudiogramForm(request.POST)
        t_formset = ThresholdFS(request.POST, queryset=Threshold.objects.none())
        if a_form.is_valid() and t_formset.is_valid():
            ag = a_form.save(commit=False)
            ag.patient = p
            ag.save()
            # guardar thresholds
            for tf in t_formset:
                th = tf.save(commit=False)
                th.audiogram = ag
                th.save()
            messages.success(request, "Audiometría guardada.")
            return redirect("patient_detail", pk=p.pk)
    else:
        a_form = AudiogramForm()
        # Cargamos 3 filas por defecto: OD Aérea, OI Aérea, (opcional) Campo Libre
        initial = [
            {"ear": "R", "pathway": "AC", "symbol": "O"},
            {"ear": "L", "pathway": "AC", "symbol": "X"},
            {"ear": "R", "pathway": "BC", "symbol": "<"},
            {"ear": "L", "pathway": "BC", "symbol": ">"},
            {"ear": "B", "pathway": "AC", "symbol": "◇"},  # Campo libre
        ]
        ThresholdFS = modelformset_factory(Threshold, form=ThresholdForm, extra=len(initial), can_delete=False)
        t_formset = ThresholdFS(queryset=Threshold.objects.none(), initial=initial)

    return render(request, "core/audiogram_form.html", {
        "a_form": a_form,
        "t_formset": t_formset,
        "patient": p
    })

# --------- Vocal / LDL ---------
@login_required
def speech_create(request, patient_pk):
    p = get_object_or_404(Patient, pk=patient_pk)
    if request.method == "POST":
        form = SpeechForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.patient = p
            s.save()
            messages.success(request, "Audiometría vocal guardada.")
            return redirect("patient_detail", pk=p.pk)
    else:
        form = SpeechForm()
    return render(request, "core/speech_form.html", {"form": form, "patient": p})

@login_required
def ldl_create(request, patient_pk):
    p = get_object_or_404(Patient, pk=patient_pk)
    if request.method == "POST":
        form = LDLForm(request.POST)
        if form.is_valid():
            l = form.save(commit=False)
            l.patient = p
            l.save()
            messages.success(request, "LDL guardado.")
            return redirect("patient_detail", pk=p.pk)
    else:
        form = LDLForm()
    return render(request, "core/ldl_form.html", {"form": form, "patient": p})
