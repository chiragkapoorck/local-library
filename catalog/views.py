from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from books.models import Book, BookInstance
from catalog.models import Owner

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
	num_users = Owner.objects.count()

	# Number of visits to this view, as counted in session variable.
	num_visits = request.session.get('num_visits', 0) # defining it to 0 because it won't be present in the first state.
	request.session['num_visits'] = num_visits + 1; 

	context = {
		'num_books': num_books,
		'num_instances':num_instances,
		'num_instances_available':num_instances_available,
		'num_users':num_users,
		'num_books_containing_the':num_books_containing_the,
		'num_visits':num_visits,
	}

	# Render the HTML template index.html with the data in the context variable
	return render(request, 'index.html', context=context)


class UserListView(generic.ListView):
	model= Owner
	template_name = 'catalog/user_list.html'
	paginate_by = 5

class UserDetailView(generic.DetailView):
	model= Owner
	template_name = 'catalog/user_detail.html'

# adding the loaned book view.
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	""" Generic class-based view listing books on loan to current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 5

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksByAllUsersListView(PermissionRequiredMixin, generic.ListView):
	""" Generic class-based view listing books on loan to current user."""
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_allusers.html'
	paginate_by = 5

	permission_required = 'catalog.can_mark_returned'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')

class UsersBookListView(LoginRequiredMixin, generic.ListView):
	""" Generic class-based view listing books on loan to current user."""
	model = Book
	template_name = 'catalog/book_list_owned_user.html'
	paginate_by = 5

	def get_queryset(self):
		return Book.objects.filter(owner=self.request.user)

class UserCreate(PermissionRequiredMixin,CreateView):
	model = Owner
	fields = '__all__'
	template_name = 'catalog/user_form.html'
	permission_required = 'catalog.can_mark_returned'

class UserUpdate(PermissionRequiredMixin,UpdateView):
	model = Owner
	fields = ['first_name', 'last_name']
	template_name = 'catalog/user_form.html'
	permission_required = 'catalog.can_mark_returned'

class UserDelete(PermissionRequiredMixin,DeleteView):
	model = Owner
	success_url = reverse_lazy('users') # why use the lazy version?
	template_name = 'catalog/user_confirm_delete.html'
	permission_required = 'catalog.can_mark_returned'

