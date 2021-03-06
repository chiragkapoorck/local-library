import datetime
from django import forms
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required

from books.models import Book, BookInstance, Genre, Language
from books.forms import RenewBookForm


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

class BookCreate(PermissionRequiredMixin, CreateView):
	model = Book
	fields = '__all__'

	def get_initial(self):
		initial = super().get_initial()
		initial.update({ "owner": self.request.user })
		return initial
	
	def get_permission_required(self):
		if self.request.user.is_authenticated:
			return ''
		return 'catalog.can_mark_returned'
	
	def form_valid(self, form):
		if not self.request.user.is_superuser:
			form.instance.owner = self.request.user
		return super().form_valid(form)

class BookUpdate(PermissionRequiredMixin, UpdateView):
	model = Book
	fields = '__all__'
	
	def get_permission_required(self):
		if self.request.user == self.get_object().owner:
			return ''
		return 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
	model = Book
	success_url = reverse_lazy('books')
	
	def get_permission_required(self):
		if self.request.user == self.get_object().owner:
			return ''
		return 'catalog.can_mark_returned'


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

	return render(request, 'book/book_renew_librarian.html', context)

@login_required
def make_request(request, pk):
	book_obj = get_object_or_404(Book, pk=pk)
	if book_obj.owner == request.user:
		messages.error(request, 'cannot request your own book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': pk}))

	instance_obj = BookInstance.objects.filter(book=book_obj, borrower=request.user, status__in=('r', 'w'))

	if instance_obj:
		messages.error(request, 'You already requsted/have the book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': pk}))
	
	new_instance = BookInstance(book = book_obj, borrower = request.user, due_back=(datetime.date.today() + datetime.timedelta(days=15)))
	new_instance.save()
	messages.success(request, 'You have successfully requested this book')

	return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': pk}))

@login_required
def accept_request(request, id):
	instance_obj = get_object_or_404(BookInstance, id=id)
	if instance_obj.book.owner != request.user:
		messages.error(request, 'cannot accept others book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))
	
	if instance_obj.status != 'r':
		messages.error(request, 'can accept only requested book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))		

	instance_obj.status = 'w'
	instance_obj.save()
	messages.success(request, 'You have accepted the request')

	return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))

@login_required
def reject_request(request, id):
	instance_obj = get_object_or_404(BookInstance, id=id)
	if instance_obj.book.owner != request.user:
		messages.error(request, 'cannot reject others book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))
	
	if instance_obj.status != 'r':
		messages.error(request, 'can reject only requested book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))		

	instance_obj.status = 'j'
	instance_obj.save()
	messages.success(request, 'You have rejected the request')

	return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))

@login_required
def book_returned(request, id):
	instance_obj = get_object_or_404(BookInstance, id=id)
	if instance_obj.book.owner != request.user:
		messages.error(request, 'cannot reject others book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))
	
	if instance_obj.status != 'w':
		messages.error(request, 'can mark return only borrowed book')
		return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))		

	instance_obj.status = 't'
	instance_obj.save()
	messages.success(request, 'You have recieved the request')

	return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': instance_obj.book.pk}))