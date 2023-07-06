from django.db import models
from django.contrib.auth.models import User




class KpiModel(models.Model):

    name = models.CharField(max_length=255)
    book = models.IntegerField()
    sport = models.IntegerField()
    work = models.DecimalField(max_digits=10, decimal_places=2)
    eureka = models.DecimalField(max_digits=10, decimal_places=2)
    general = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    league = models.CharField(max_length=255, null=True, blank=True)
    koef = models.DecimalField(max_digits=10, decimal_places=2)
    book_comment = models.URLField(max_length=255, null=True)

    def calculate_general(self):
        total_sum = self.sport + self.book + float(self.eureka) + float(self.work)

        if total_sum <= 10:
            result = total_sum
        elif total_sum <= 23:
            result = 10 + 0.8 * (total_sum - 10)
        elif total_sum <= 39:
            result = 10.4 + 0.6 * (total_sum - 23)
        elif total_sum <= 64:
            result = 9.6 + 0.4 * (total_sum - 39)
        elif total_sum <= 114:
            result = 10 + 0.2 * (total_sum - 64)
        elif total_sum <= 181:
            result = 10 + 0.15 * (total_sum - 114)
        elif total_sum < 281:
            result = 10.05 + 0.1 * (total_sum - 181)
        else:
            result = 9.95

        self.general = 50 + result

    def get_league(self):
        if self.general < 40:
            return "REJECTED"
        elif self.general < 60:
            return "WOOD"
        elif self.general < 70:
            return "STONE"
        elif self.general < 80:
            return "BRONZE"
        elif self.general < 90:
            return "SILVER"
        elif self.general < 100:
            return "CRYSTAL"
        elif self.general < 110:
            return "ELITE"
        else:
            return "LEGEND"

    def get_koef(self):
        if self.sport < 40:
            return 0
        elif self.sport < 60:
            return 1
        elif self.sport < 70:
            return 0.8
        elif self.sport < 80:
            return 0.6
        elif self.sport < 90:
            return 0.4
        elif self.sport < 100:
            return 0.2
        elif self.sport < 110:
            return 0.15
        else:
            return 0.1

    def save(self, *args, **kwargs):
        self.calculate_general()

        self.league = self.get_league()
        self.koef = self.get_koef()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name', 'book', 'sport', 'work','eureka', 'general', 'league', 'koef']


    def __str__(self):
        return f"{self.name} {self.book} {self.sport} {self.work} {self.eureka} {self.general} {self.league} {self.koef}"



