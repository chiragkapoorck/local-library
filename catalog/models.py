from django.urls import reverse 
# adding connection between users and book_instances
from django.contrib.auth.models import User

# Create your models here.

# Model representing an Owner
class Owner(User):
	class Meta:
		proxy = True
		ordering = ['last_name', 'first_name']

	def get_absolute_url(self):
		"""Returns the url to access a particular user instance."""
		return reverse('user-detail', args=[str(self.id)])

	def __str__(self):
		"""String for representing the Model object."""
		return f'{self.last_name}, {self.first_name}'