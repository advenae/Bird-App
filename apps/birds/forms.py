from django import forms
from django.core.exceptions import ValidationError
from .models import Biotop, Kolor


MIESIACE = [
    ("", ""),
    (1, "styczeń"), (2, "luty"), (3, "marzec"), (4, "kwiecień"),
    (5, "maj"), (6, "czerwiec"), (7, "lipiec"), (8, "sierpień"),
    (9, "wrzesień"), (10, "październik"), (11, "listopad"), (12, "grudzień"),
]


class ObserwacjaForm(forms.Form):
    biotop = forms.ModelChoiceField(
        queryset=Biotop.objects.all(),
        required=False,
        label="Biotop",
        empty_label="",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    miesiac = forms.ChoiceField(
        choices=MIESIACE,
        required=False,
        label="Miesiąc obserwacji",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    dlugosc_ciala = forms.FloatField(
        required=False,
        label="Długość ciała (cm)",
        min_value=0.1,
        max_value=300,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    rozpietosc_skrzydel = forms.FloatField(
        required=False,
        label="Rozpiętość skrzydeł (cm)",
        min_value=0.1,
        max_value=400,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    kolory = forms.ModelMultipleChoiceField(
        queryset=Kolor.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}),
        label="Zaobserwowane kolory",
    )

    def clean(self):
        cleaned_data = super().clean()
        podano_cokolwiek = any([
            cleaned_data.get("biotop"),
            cleaned_data.get("miesiac"),
            cleaned_data.get("dlugosc_ciala"),
            cleaned_data.get("rozpietosc_skrzydel"),
            cleaned_data.get("kolory"),
        ])
        if not podano_cokolwiek:
            raise ValidationError("Podaj przynajmniej jedno kryterium obserwacji.")
        return cleaned_data