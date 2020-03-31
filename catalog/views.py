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


# Creating the view for FORM
import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
	book_instance = get_object_or_404(BookInstance, pk=pk)

	# If this is a POST request then process the Form data
	if request.method == 'POST':

		# Create a form instance and populate it with the data from the request (binding):
		form = RenewBookForm(request.POST)

		# Check if the form is valid
		if form.is_valid():
			# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			# redirect to a new URL:
			return HttpResponseRedirect(reverse('all-borrowed'))

	# If this is a GET (or any other method) create the default form.
	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

	context = {
		'form': form,
		'book_instance': book_instance,

	}

	return render(request, 'catalog/book_renew_librarian.html', context)

# Editing Views
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class AuthorCreate(PermissionRequiredMixin,CreateView):
	model = Author
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
	model = Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
	permission_required = 'catalog.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin,DeleteView):
	model = Author
	success_url = reverse_lazy('authors') # why use the lazy version?
	permission_required = 'catalog.can_mark_returned'

class BookCreate(PermissionRequiredMixin, CreateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
	model = Book
	success_url = reverse_lazy('books')
	permission_required = 'catalog.can_mark_returned'
