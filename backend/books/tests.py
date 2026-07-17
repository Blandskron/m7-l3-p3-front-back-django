from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from authors.models import Author
from categories.models import Category
from profiles.models import MemberProfile

from .models import Book, BookCategory


class LibraryRelationshipTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Gabriel García Márquez")
        self.book = Book.objects.create(
            title="Cien años de soledad",
            isbn="9780307474728",
            author=self.author,
        )

    def test_many_to_one_and_cascade_delete(self):
        Book.objects.create(title="El amor", isbn="9780307389732", author=self.author)
        self.assertEqual(self.author.books.count(), 2)
        self.author.delete()
        self.assertEqual(Book.objects.count(), 0)

    def test_many_to_many_uses_intermediate_model_with_extra_fields(self):
        category = Category.objects.create(name="Novela")
        assignment = BookCategory.objects.create(
            book=self.book, category=category, priority=2
        )
        self.assertIn(category, self.book.categories.all())
        self.assertEqual(assignment.priority, 2)
        with self.assertRaises(IntegrityError), transaction.atomic():
            BookCategory.objects.create(book=self.book, category=category)

    def test_one_to_one_profile_is_unique_and_bidirectional(self):
        user = User.objects.create_user(username="socia", password="test-password")
        profile = MemberProfile.objects.create(
            user=user,
            membership_id="SOC-001",
            address="Santiago",
            phone="+56911111111",
        )
        self.assertEqual(user.member_profile, profile)
        with self.assertRaises(IntegrityError), transaction.atomic():
            MemberProfile.objects.create(
                user=user, membership_id="SOC-002", address="Valparaíso", phone="123"
            )


class LibraryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = Author.objects.create(name="Isabel Allende")

    def test_create_book_with_category_assignment(self):
        response = self.client.post(
            "/api/v1/books/",
            {
                "title": "La casa de los espíritus",
                "isbn": "9788401352898",
                "author_id": self.author.pk,
                "categories_input": [{"name": "Novela", "priority": 3}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["category_assignments"][0]["priority"], 3)

    def test_main_routes_and_profile_endpoint_are_accessible(self):
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/docs/swagger/").status_code, 200)
        self.assertEqual(self.client.get("/admin/").status_code, 302)
        self.assertEqual(self.client.get("/api/v1/profiles/").status_code, 200)
