from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from .views import _parse_categories_text


class WebTests(TestCase):
    def test_category_parser_deduplicates_and_keeps_highest_priority(self):
        result = _parse_categories_text("Novela:1, Historia, novela:3")
        self.assertEqual(result, [{"name": "novela", "priority": 3}, {"name": "Historia", "priority": 1}])

    @patch("web.views.requests.get")
    def test_books_page_renders_api_data(self, mocked_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = [{"title": "Libro", "isbn": "123"}]
        mocked_get.return_value = response
        page = self.client.get(reverse("books_list"))
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Libro")
