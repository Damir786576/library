from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from .forms import BookForm
from .models import Book


class IndexView(TemplateView):
    template_name = 'index.html'


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'create_book.html'
    success_url = '/books/'


class BookListView(ListView):
    model = Book
    form_class = BookForm
    template_name = 'list_book.html'


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'update_book.html'


class BookDeleteView(DeleteView):
    model = Book
    form_class = BookForm
    template_name = 'delete_book.html'
