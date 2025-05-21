from django.core.validators import MinValueValidator
from django.db import models

from reader.models import Reader


class Book(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    author = models.CharField(max_length=100, blank=False, null=False)
    year = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    amount = models.IntegerField(default=1,
                                 validators=[MinValueValidator(
                                     0, "Количество экземпляров не может быть меньше 0")])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"


class BorrowedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowed_books')
    reader = models.ForeignKey(Reader, on_delete=models.CASCADE, related_name='borrowed_books')
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.book.name} borrowed by {self.reader.name}"

    class Meta:
        verbose_name = "Borrowed Book"
        verbose_name_plural = "Borrowed Books"
