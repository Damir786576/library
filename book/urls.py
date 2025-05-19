from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('books/create/', views.BookCreateView.as_view(), name='create_book'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
]
