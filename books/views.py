from django.shortcuts import render
from books.models import Book, BookInstance, Genre, Language
from django.views import generic


# Create your views here.
class BookListView(generic.ListView):
    model=Book
    paginate_by = 5
    template_name = 'books/book_list.html'
	# context_object_name = 'my_book_list' # your own name for the list as a template variable
	# queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
	# template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location

# Defining another class-based view. // for book-detail view.
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

