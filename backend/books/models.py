from django.db import models
from authors.models import Author
from categories.models import Category


class Book(models.Model):
    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
    )
    published_date = models.DateField(null=True, blank=True)
    categories = models.ManyToManyField(
        Category,
        through="BookCategory",
        related_name="books",
    )

    class Meta:
        db_table = "book"

    def __str__(self):
        return self.title
    
class BookCategory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    assigned_at = models.DateField(auto_now_add=True)
    priority = models.PositiveSmallIntegerField(default=1)

    class Meta:
        db_table = "book_category"
        constraints = [
            models.UniqueConstraint(
                fields=("book", "category"), name="unique_book_category"
            )
        ]

    def __str__(self):
        return f"{self.book.title} - {self.category.name}"
