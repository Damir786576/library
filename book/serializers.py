from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Book, BorrowedBook
from reader.models import Reader


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'year', 'isbn', 'amount']


class BorrowedBookSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    reader = serializers.PrimaryKeyRelatedField(queryset=Reader.objects.all())

    class Meta:
        model = BorrowedBook
        fields = ['id', 'book', 'reader', 'borrow_date', 'return_date']

    def validate(self, data):
        book = data['book']
        reader = data['reader']

        # Бизнес-логика 1: Проверка на доступные экземпляры
        if book.amount <= 0:
            raise serializers.ValidationError("Нет доступных экземпляров книги для выдачи.")

        # Бизнес-логика 2: Проверка на максимум 3 книги у читателя
        active_borrows = BorrowedBook.objects.filter(reader=reader, return_date__isnull=True).count()
        if active_borrows >= 3:
            raise serializers.ValidationError("Читатель не может взять более 3 книг одновременно.")

        return data
