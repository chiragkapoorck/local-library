from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('users/', views.UserListView.as_view(), name='users'),
	path('user/<int:pk>', views.UserDetailView.as_view(), name='user-detail'),
	path('my_borrowed/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
	path('my_books/', views.UsersBookListView.as_view(), name='my-books'),
	path('all_books/', views.LoanedBooksByAllUsersListView.as_view(), name="all-borrowed"),
	path('user/create/', views.UserCreate.as_view(), name='user-create'),
	path('user/<int:pk>/update/', views.UserUpdate.as_view(), name='user-update'),
	path('user/<int:pk>/delete/', views.UserDelete.as_view(), name='user-delete'),
	
]