from django.core.validators import EmailValidator
from django.db import models


class Reader(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    email = models.CharField(max_length=255, blank=False, null=False, unique=True,
                             validators=[EmailValidator(message="Введите действительный email")])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Reader"
        verbose_name_plural = "Readers"
