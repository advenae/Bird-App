from django.shortcuts import render, get_object_or_404
from .forms import ObserwacjaForm
from .models import Gatunek


# Wagi kryteriów wyznaczone metodą ROC (5)
WAGI = {
    "biotop": 0.456667,
    "miesiac": 0.256667,
    "dlugosc_ciala": 0.1567,
    "rozpietosc_skrzydel": 0.09,
    "kolory": 0.04,
}


# Funkcja przynależności dla cech liczbowych (6) i (7)
def przynaleznosc_trapezoidalna(x, a, b):
    t = (a + b) / 4
    if x < a - t:
        return 0.0
    elif x < a:
        return (x - (a - t)) / t
    elif x <= b:
        return 1.0
    elif x <= b + t:
        return ((b + t) - x) / t
    else:
        return 0.0


def miesiac_w_zakresie(miesiac, od, do):
    if od <= do:
        return od <= miesiac <= do
    return miesiac >= od or miesiac <= do

# Stopień podzbiorowości (8)
def zgodnosc_ubarwienia(kolory_uzytkownika, kolory_gatunku):
    wspolne = kolory_uzytkownika & kolory_gatunku
    return len(wspolne) / len(kolory_uzytkownika)

# Renormalizacja i przeliczenie wag (9)
def przelicz_wagi(dane):
    uzyte = {klucz: WAGI[klucz] for klucz, wartosc in dane.items() if wartosc}
    suma = sum(uzyte.values())
    if suma == 0:
        return {}
    return {klucz: waga / suma for klucz, waga in uzyte.items()}

# Ranking na podstawie oceny SAW dla wszystkich gatunków (4) lub (10)
def oblicz_ranking_SAW(dane):
    wagi = przelicz_wagi(dane)
    if not wagi:
        return []

    wyniki = []
    for gatunek in Gatunek.objects.prefetch_related("biotopy", "kolory"):
        ocena = 0.0

        if "biotop" in wagi:
            zgodnosc = 1.0 if gatunek.biotopy.filter(pk=dane["biotop"].pk).exists() else 0.0
            ocena += wagi["biotop"] * zgodnosc

        if "miesiac" in wagi:
            zgodnosc = 1.0 if miesiac_w_zakresie(int(dane["miesiac"]), gatunek.miesiac_od, gatunek.miesiac_do) else 0.0
            ocena += wagi["miesiac"] * zgodnosc

        if "dlugosc_ciala" in wagi:
            zgodnosc = przynaleznosc_trapezoidalna(dane["dlugosc_ciala"], gatunek.dlugosc_ciala_min, gatunek.dlugosc_ciala_max)
            ocena += wagi["dlugosc_ciala"] * zgodnosc

        if "rozpietosc_skrzydel" in wagi:
            zgodnosc = przynaleznosc_trapezoidalna(dane["rozpietosc_skrzydel"], gatunek.rozpietosc_skrzydel_min, gatunek.rozpietosc_skrzydel_max)
            ocena += wagi["rozpietosc_skrzydel"] * zgodnosc

        if "kolory" in wagi:
            kolory_gatunku = set(gatunek.kolory.all())
            zgodnosc = zgodnosc_ubarwienia(set(dane["kolory"]), kolory_gatunku)
            ocena += wagi["kolory"] * zgodnosc

        wyniki.append((gatunek, round(ocena, 3)))

    wyniki.sort(key=lambda para: para[1], reverse=True)
    return wyniki


def home(request):
    form = ObserwacjaForm(request.POST or None)
    wyniki = None

    if request.method == "POST" and form.is_valid():
        dane = {
            "biotop": form.cleaned_data.get("biotop"),
            "miesiac": form.cleaned_data.get("miesiac"),
            "dlugosc_ciala": form.cleaned_data.get("dlugosc_ciala"),
            "rozpietosc_skrzydel": form.cleaned_data.get("rozpietosc_skrzydel"),
            "kolory": form.cleaned_data.get("kolory"),
        }
        wyniki = oblicz_ranking_SAW(dane)

    return render(request, "birds/home.html", {"form": form, "wyniki": wyniki})

def o_serwisie(request):
    return render(request, "birds/o_serwisie.html")


def gatunek_szczegoly(request, pk):
    gatunek = get_object_or_404(Gatunek, pk=pk)
    return render(request, "birds/gatunek_szczegoly.html", {"gatunek": gatunek})