import os
import django
from django.conf import settings

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from book.models import Book, BorrowedBook
from reader.models import Reader

# Настройка Django перед тестами
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


class LibraryAPITests(APITestCase):
    def setUp(self):
        # Создаём пользователя для тестов
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword123'
        )
        # Получаем токен для пользователя
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': 'testuser', 'password': 'testpassword123'},
            format='json'
        )
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Создаём тестовые данные
        self.book = Book.objects.create(
            name='Test Book',
            author='Test Author',
            year=2020,
            isbn='1234567890123',
            amount=3
        )
        self.reader = Reader.objects.create(
            name='Test Reader',
            email='reader@example.com'
        )

    def test_register_user(self):
        """Тест регистрации нового пользователя"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Один пользователь из setUp + новый

    def test_get_all_books_public(self):
        """Тест получения списка всех книг (публичный)"""
        url = reverse('book_list')
        # Убираем токен, так как эндпоинт публичный
        self.client.credentials()
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Одна книга из setUp

    def test_create_book_authenticated(self):
        """Тест создания книги (требуется аутентификация)"""
        url = reverse('book_list')
        data = {
            'name': 'New Book',
            'author': 'New Author',
            'year': 2021,
            'isbn': '9876543210123',
            'amount': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)  # Одна книга из setUp + новая

    def test_create_reader_authenticated(self):
        """Тест создания читателя (требуется аутентификация)"""
        url = reverse('reader_list')
        data = {
            'name': 'New Reader',
            'email': 'newreader@example.com'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reader.objects.count(), 2)  # Один читатель из setUp + новый

    def test_borrow_book(self):
        """Тест выдачи книги читателю"""
        url = reverse('borrow_book')
        data = {
            'book': self.book.id,
            'reader': self.reader.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.amount, 2)  # Количество уменьшилось на 1
        self.assertEqual(BorrowedBook.objects.count(), 1)

    def test_borrow_book_limit_exceeded(self):
        """Тест на превышение лимита (3 книги на читателя)"""
        # Выдаём 3 книги
        for i in range(3):
            book = Book.objects.create(
                name=f'Book {i}',
                author='Author',
                year=2020,
                isbn=f'111111111{i:03d}',
                amount=1
            )
            self.client.post(
                reverse('borrow_book'),
                {'book': book.id, 'reader': self.reader.id},
                format='json'
            )

        # Пытаемся выдать четвёртую книгу
        response = self.client.post(
            reverse('borrow_book'),
            {'book': self.book.id, 'reader': self.reader.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не может взять более 3 книг', str(response.data))

    def test_return_book(self):
        """Тест возврата книги"""
        # Сначала выдаём книгу
        borrow_response = self.client.post(
            reverse('borrow_book'),
            {'book': self.book.id, 'reader': self.reader.id},
            format='json'
        )
        borrow_id = borrow_response.data['id']

        # Возвращаем книгу
        url = reverse('return_book', kwargs={'pk': borrow_id})
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.amount, 3)  # Количество вернулось

    def test_get_reader_borrowed_books(self):
        """Тест получения списка книг, взятых читателем (ещё не возвращённых)"""
        # Выдаём книгу
        self.client.post(
            reverse('borrow_book'),
            {'book': self.book.id, 'reader': self.reader.id},
            format='json'
        )

        # Получаем список взятых книг
        url = reverse('reader_borrowed_books', kwargs={'reader_id': self.reader.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Одна книга
        self.assertEqual(response.data[0]['name'], 'Test Book')

    def test_borrowed_books_authentication(self):
        """Тест проверки JWT-аутентификации для защищённого эндпоинта"""
        # Выдаём книгу, чтобы у читателя была хотя бы одна книга
        self.client.post(
            reverse('borrow_book'),
            {'book': self.book.id, 'reader': self.reader.id},
            format='json'
        )

        # Проверяем доступ без токена
        self.client.credentials()  # Убираем токен
        url = reverse('reader_borrowed_books', kwargs={'reader_id': self.reader.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')

        # Проверяем доступ с токеном
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Одна книга
        self.assertEqual(response.data[0]['name'], 'Test Book')
