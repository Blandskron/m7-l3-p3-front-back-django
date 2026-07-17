from django.contrib import admin
from .models import Book, BookCategory


class BookCategoryInline(admin.TabularInline):
    model = BookCategory
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn")
    list_select_related = ("author",)
    search_fields = ("title", "isbn", "author__name")
    inlines = (BookCategoryInline,)

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ("book", "category", "priority", "assigned_at")
    list_select_related = ("book", "category")
