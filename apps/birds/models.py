from django.db import models


class Biotop(models.Model):
    nazwa = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nazwa


class Kolor(models.Model):
    nazwa = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nazwa


class Gatunek(models.Model):
    nazwa = models.CharField(max_length=150)

    biotopy = models.ManyToManyField(Biotop, related_name="gatunki")

    kolory = models.ManyToManyField(Kolor, related_name="gatunki")

    dlugosc_ciala_min = models.FloatField(help_text="cm")
    dlugosc_ciala_max = models.FloatField(help_text="cm")

    rozpietosc_skrzydel_min = models.FloatField(help_text="cm")
    rozpietosc_skrzydel_max = models.FloatField(help_text="cm")

    miesiac_od = models.PositiveSmallIntegerField(help_text="1-12")
    miesiac_do = models.PositiveSmallIntegerField(help_text="1-12")

    def __str__(self):
        return self.nazwa