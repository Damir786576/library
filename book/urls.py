from django.urls import path
from . import views

urlpatterns = [
    path('api/register/', views.RegisterView.as_view()),
    path('api/books/', views.BookListCreateAPIView.as_view()),
    path('api/books/<int:pk>/', views.BookRetrieveUpdateDestroyAPIView.as_view()),
    path('api/borrow/', views.BorrowBookAPIView.as_view()),
    path('api/return/<int:pk>/', views.ReturnBookAPIView.as_view()),
    path('api/readers/<int:reader_id>/borrowed-books/', views.ReaderBorrowedBooksAPIView.as_view())
]
