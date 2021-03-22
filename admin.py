from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import books,manage_books,students,employees,newspaper,manage_bookbank,bookbank
@admin.register(books)
@admin.register(manage_books)
@admin.register(students)
@admin.register(employees)
@admin.register(newspaper)
@admin.register(manage_bookbank)
@admin.register(bookbank)
class ViewAdmin(ImportExportModelAdmin):
    pass