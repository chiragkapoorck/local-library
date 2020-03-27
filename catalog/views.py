from django.shortcuts import render

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre, Language

# View function for home page of sites.
def index(request):
	# Generates counts of some of the main objects
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	# Available Books (status = 'a')
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()

	# Books containing the word "the" // should be case-insensitive.
	num_books_containing_the = Book.objects.filter(title__contains='the').count()

	# The 'all()' is implied by default
	num_authors = Author.objects.count()

	# Number of visits to this view, as counted in session variable.
	num_visits = request.session.get('num_visits', 0) # defining it to 0 because it won't be present in the first state.
	request.session['num_visits'] = num_visits + 1; 

	context = {
		'num_books': num_books,
		'num_instances':num_instances,
		'num_instances_available':num_instances_available,
		'num_authors':num_authors,
		'num_books_containing_the':num_books_containing_the,
		'num_visits':num_visits,
	}

	# Render the HTML template index.html with the data in the context variable
	return render(request, 'index.html', context=context)

# Defining a class-based view.
from django.views import generic

class BookListView(generic.ListView):
	model=Book
	paginate_by = 5
	# context_object_name = 'my_book_list' # your own name for the list as a template variable
	# queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
	# template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location

# Defining another class-based view. // for book-detail view.
class BookDetailView(generic.DetailView):
	model = Book

class AuthorListView(generic.ListView):
	model=Author
	paginate_by = 5

class AuthorDetailView(generic.DetailView):
	model=Author

# adding the loaned book view.
from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	""" Generic class-based view listing books on loan to current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 5

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from django.contrib.auth.mixins import PermissionRequiredMixin

class LoanedBooksByAllUsersListView(PermissionRequiredMixin, generic.ListView):
	""" Generic class-based view listing books on loan to current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_allusers.html'
	paginate_by = 5

	permission_required = 'catalog.can_mark_returned'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')
