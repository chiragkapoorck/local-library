import datetime
from django.shortcuts import render
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required

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
	permission_required = 'catalog.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
	model = Book
	success_url = reverse_lazy('books')
	permission_required = 'catalog.can_mark_returned'


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
