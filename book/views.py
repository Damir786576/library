from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import Book, BorrowedBook
from .serializers import BookSerializer, RegisterSerializer, BorrowedBookSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class BookListCreateAPIView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]


class BookRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class BorrowBookAPIView(generics.CreateAPIView):
    queryset = BorrowedBook.objects.all()
    serializer_class = BorrowedBookSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        book = instance.book
        book.amount -= 1
        book.save()


class ReturnBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            # Находим запись о выдаче по ID
            borrowed_book = BorrowedBook.objects.get(pk=pk)

            # Бизнес-логика 3: Проверяем, что книга ещё не возвращена
            if borrowed_book.return_date is not None:
                return Response(
                    {"error": "Книга уже была возвращена."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Устанавливаем дату возврата
            borrowed_book.return_date = timezone.now()
            borrowed_book.save()

            # Увеличиваем количество экземпляров книги
            book = borrowed_book.book
            book.amount += 1
            book.save()

            return Response(
                {"message": "Книга успешно возвращена."},
                status=status.HTTP_200_OK
            )

        except BorrowedBook.DoesNotExist:
            return Response(
                {"error": "Запись о выдаче не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )


class ReaderBorrowedBooksAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reader_id):
        # Получаем все записи о выдаче для читателя, где книга ещё не возвращена
        borrowed_books = BorrowedBook.objects.filter(
            reader_id=reader_id,
            return_date__isnull=True
        )
        # Извлекаем книги из записей о выдаче
        books = [borrowed_book.book for borrowed_book in borrowed_books]
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
