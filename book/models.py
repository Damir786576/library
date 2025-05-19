from django.db import models


class Book(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    author = models.CharField(max_length=100, blank=False, null=False)
    year = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    amount = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
