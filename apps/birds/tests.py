from django.test import TestCase
from .views import (
    przynaleznosc_trapezoidalna,
    miesiac_w_zakresie,
    zgodnosc_ubarwienia,
    przelicz_wagi,
    oblicz_ranking_SAW,
)
from .models import Biotop, Kolor, Gatunek


class PrzynaleznoscTrapezoidalnaTest(TestCase):

    def test_wartosc_w_srodku_zakresu_daje_pelna_zgodnosc(self):
        self.assertEqual(przynaleznosc_trapezoidalna(11, 10, 12), 1.0)

    def test_wartosc_na_granicy_zakresu_daje_pelna_zgodnosc(self):
        self.assertEqual(przynaleznosc_trapezoidalna(10, 10, 12), 1.0)
        self.assertEqual(przynaleznosc_trapezoidalna(12, 10, 12), 1.0)

    def test_wartosc_poza_tolerancja_daje_zero(self):
        self.assertEqual(przynaleznosc_trapezoidalna(4, 10, 12), 0.0)
        self.assertEqual(przynaleznosc_trapezoidalna(18, 10, 12), 0.0)

    def test_wartosc_posrednia_ponizej_zakresu(self):
        wynik = przynaleznosc_trapezoidalna(7.25, 10, 12)
        self.assertAlmostEqual(wynik, 0.5, places=3)

    def test_wartosc_posrednia_powyzej_zakresu(self):
        wynik = przynaleznosc_trapezoidalna(14.75, 10, 12)
        self.assertAlmostEqual(wynik, 0.5, places=3)


class MiesiacWZakresieTest(TestCase):

    def test_zakres_zwykly(self):
        self.assertTrue(miesiac_w_zakresie(6, 4, 9))
        self.assertFalse(miesiac_w_zakresie(11, 4, 9))

    def test_zakres_przez_przelom_roku(self):
        self.assertTrue(miesiac_w_zakresie(12, 11, 2))
        self.assertTrue(miesiac_w_zakresie(1, 11, 2))
        self.assertFalse(miesiac_w_zakresie(6, 11, 2))

    def test_caly_rok(self):
        for m in range(1, 13):
            self.assertTrue(miesiac_w_zakresie(m, 1, 12))


class ZgodnoscUbarwieniaTest(TestCase):

    def test_pelna_zgodnosc(self):
        wynik = zgodnosc_ubarwienia({"czarny", "biały"}, {"czarny", "biały"})
        self.assertEqual(wynik, 1.0)

    def test_zgodnosc(self):
            wynik = zgodnosc_ubarwienia({"czarny", "biały"}, {"czarny", "biały", "szary"})
            self.assertEqual(wynik, 1.0)

    def test_czesciowa_zgodnosc(self):
        wynik = zgodnosc_ubarwienia({"czarny", "biały"}, {"czarny", "szary"})
        self.assertEqual(wynik, 0.5)

    def test_brak_zgodnosci(self):
        wynik = zgodnosc_ubarwienia({"czerwony"}, {"czarny", "biały"})
        self.assertEqual(wynik, 0.0)


class PrzeliczWagiTest(TestCase):

    def test_wszystkie_kryteria_podane_sumuja_sie_do_jednego(self):
        dane = {
            "biotop": "las", "miesiac": "6",
            "dlugosc_ciala": 15, "rozpietosc_skrzydel": 25,
            "kolory": ["czarny"],
        }
        wagi = przelicz_wagi(dane)
        self.assertAlmostEqual(sum(wagi.values()), 1.0, places=6)

    def test_tylko_jedno_kryterium_daje_wage_jeden(self):
        dane = {"biotop": "las", "miesiac": None, "dlugosc_ciala": None,
                "rozpietosc_skrzydel": None, "kolory": None}
        wagi = przelicz_wagi(dane)
        self.assertEqual(wagi, {"biotop": 1.0})

    def test_brak_kryteriow_daje_pusty_slownik(self):
        dane = {"biotop": None, "miesiac": None, "dlugosc_ciala": None,
                "rozpietosc_skrzydel": None, "kolory": None}
        self.assertEqual(przelicz_wagi(dane), {})

    def test_zachowuje_proporcje_wag(self):
        dane = {"biotop": "las", "miesiac": None, "dlugosc_ciala": None,
                "rozpietosc_skrzydel": None, "kolory": ["czarny"]}
        wagi = przelicz_wagi(dane)
        proporcja_oryginalna = 0.456667 / 0.04
        proporcja_po_przeliczeniu = wagi["biotop"] / wagi["kolory"]
        self.assertAlmostEqual(proporcja_oryginalna, proporcja_po_przeliczeniu, places=3)


class ObliczRankingSAWTest(TestCase):
    """Testy integracyjne - wymagają prawdziwych obiektów w bazie testowej."""

    def setUp(self):
        self.las = Biotop.objects.create(nazwa="las")
        self.miasto = Biotop.objects.create(nazwa="miasto")
        self.czarny = Kolor.objects.create(nazwa="czarny")
        self.szary = Kolor.objects.create(nazwa="szary")

        self.wrobel = Gatunek.objects.create(
            nazwa="Wróbel",
            dlugosc_ciala_min=14, dlugosc_ciala_max=16,
            rozpietosc_skrzydel_min=21, rozpietosc_skrzydel_max=25,
            miesiac_od=1, miesiac_do=12,
        )
        self.wrobel.biotopy.add(self.miasto)
        self.wrobel.kolory.add(self.czarny, self.szary)

        self.bocian = Gatunek.objects.create(
            nazwa="Bocian",
            dlugosc_ciala_min=100, dlugosc_ciala_max=115,
            rozpietosc_skrzydel_min=155, rozpietosc_skrzydel_max=165,
            miesiac_od=3, miesiac_do=9,
        )
        self.bocian.biotopy.add(self.las)

    def test_dopasowanie_po_biotopie_stawia_wlasciwy_gatunek_wyzej(self):
        dane = {"biotop": self.miasto, "miesiac": None, "dlugosc_ciala": None,
                "rozpietosc_skrzydel": None, "kolory": None}
        wyniki = oblicz_ranking_SAW(dane)
        # wróbel (biotop=miasto) powinien być wyżej niż bocian (biotop=las)
        gatunki_w_kolejnosci = [g.nazwa for g, ocena in wyniki]
        self.assertEqual(gatunki_w_kolejnosci[0], "Wróbel")

    def test_pusta_baza_kryteriow_zwraca_pusta_liste(self):
        dane = {"biotop": None, "miesiac": None, "dlugosc_ciala": None,
                "rozpietosc_skrzydel": None, "kolory": None}
        self.assertEqual(oblicz_ranking_SAW(dane), [])

    def test_wynik_zawsze_w_przedziale_0_1(self):
        dane = {"biotop": self.las, "miesiac": "6",
                "dlugosc_ciala": 50, "rozpietosc_skrzydel": 100,
                "kolory": [self.czarny]}
        wyniki = oblicz_ranking_SAW(dane)
        for gatunek, ocena in wyniki:
            self.assertGreaterEqual(ocena, 0.0)
            self.assertLessEqual(ocena, 1.0)