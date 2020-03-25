from django.db import models

# Create your models here.

"""model representing a book genre"""
class Genre(models.Model):
	name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

	def __str__(self):
		"""string for representing the Model object."""
		return self.name

class Language(models.Model):
	lang = models.CharField(max_length=100, help_text='Enter the language for this book')

	def __str__(self):
		return self.lang

# Used to generate URLs by reversing the URL pattern.
from django.urls import reverse 

"""Model representing a Book (but not a specified copy of a book)."""
class Book(models.Model):
	title = models.CharField(max_length=200)

	# Foreign key used because book can only have one author but a single author can have many books
	# Author as a string rather than object because it hasn't been yet declared in a file.
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

	summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
	isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

	# Many to Many Field used because a genre can contain many books. And a book can have many genres.
	# Genre class has already been defined so we can specify the object here.
	genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

	def display_genre(self):
		"""Create a string for the Genre. This is required to display genre in Admin."""
		return ', '.join(genre.name for genre in self.genre.all()[:3])

	display_genre.shirt_description = 'Genre'

	def __str__(self):
		"""string for representing the model object"""
		return self.title

	def get_absolute_url(self):
		"""Returns a URL to get detailed access to a book"""
		return reverse('book-detail', args=[str(self.id)])

import uuid # Required for unique book instances

# Model representing a specific copy of a book (meaning it can be borrowed from the library)
class BookInstance(models.Model):
	id = models.UUIDField(primary_key = True, default=uuid.uuid4, help_text='unique id for a book across the whole library')
	book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True) # I think book should be there as it has already been defined above as a class
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)
	language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

	LOAN_STATUS = (
		('m', 'Maintainance'),
		('o', 'On Loan'),
		('a', 'Available'),
		('r', 'Reserved'),
	) 

	status = models.CharField(
		max_length=1,
		choices=LOAN_STATUS,
		blank=True,
		default='m',
		help_text='book availability',
	)

	class Meta:
		ordering = ['due_back']

	def __str__(self):
		# String for representing the model object
		return f'{self.id} ({self.book.title})'

# Model representing an Author
class Author(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(null=True, blank=True)
	date_of_death = models.DateField('Died', null=True, blank=True)

	class Meta:
		ordering = ['last_name', 'first_name']

	def get_absolute_url(self):
		"""Returns the url to access a particular author instance."""
		return reverse('author-detail', args=[str(self.id)])

	def __str__(self):
		"""String for representing the Model object."""
		return f'{self.last_name}, {self.first_name}'



