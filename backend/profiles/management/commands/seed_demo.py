from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from authors.models import Author
from books.models import Book, BookCategory
from categories.models import Category
from profiles.models import MemberProfile


class Command(BaseCommand):
    help = "Crea datos de demostración idempotentes para las tres relaciones ORM."

    @transaction.atomic
    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username="socia_demo")
        MemberProfile.objects.update_or_create(
            user=user,
            defaults={
                "membership_id": "SOC-001",
                "address": "Santiago de Chile",
                "phone": "+56911111111",
            },
        )
        author, _ = Author.objects.get_or_create(name="Isabel Allende")
        book, _ = Book.objects.update_or_create(
            isbn="9788401352898",
            defaults={"title": "La casa de los espíritus", "author": author},
        )
        category, _ = Category.objects.get_or_create(name="Novela")
        BookCategory.objects.update_or_create(
            book=book, category=category, defaults={"priority": 1}
        )
        self.stdout.write(self.style.SUCCESS("Datos de demostración listos."))
