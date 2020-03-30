from django.contrib import admin

# Register your models here.
from .models import Genre, Language, Book, BookInstance

admin.site.register(Genre)
admin.site.register(Language)
#admin.site.register(Book)
#admin.site.register(BookInstance)

class BookInline(admin.TabularInline):
	model = Book
	fields = ['title','summary','isbn','genre'] # why is this not showing vertically stacked!
	extra = 1

class BooksInstanceInline(admin.TabularInline):
	model = BookInstance
	extra = 0

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ('title', 'authors', 'owner', 'display_genre') # won't directly use genre as it's a many-to-many field.
	inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
	list_display = ('book', 'status', 'borrower', 'due_back', 'id')
	list_filter = ('status', 'due_back')

	fieldsets = (
		(None, {
			'fields': ('book', 'imprint', 'id')
			}),
		('Availability', {
			'fields': ('status', 'due_back', 'borrower')
			}),
		)