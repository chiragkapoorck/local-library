from django.urls import path
from . import views

urlpatterns = [
	path('books/', views.BookListView.as_view(), name='books'),
	path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
	path('book/create/', views.BookCreate.as_view(), name='book-create'),
	path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
	path('book/request/<int:pk>/', views.make_request, name='book-request'),
	path('book/request/accept/<uuid:id>', views.accept_request, name='accept-request'),
	path('book/request/reject/<uuid:id>', views.reject_request, name='reject-request'),
	path('book/returned/<uuid:id>/', views.book_returned, name='book-returned'),
	path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
	path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'), # why did we use uuid instead of int? because we are referring to book instance rather than the book itself.

]