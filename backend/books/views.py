from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, BookCategory
from categories.models import Category
from .serializers import BookSerializer, BookCategorySerializer


@extend_schema_view(
    list=extend_schema(tags=["Books"]),
    retrieve=extend_schema(tags=["Books"]),
    create=extend_schema(tags=["Books"]),
    update=extend_schema(tags=["Books"]),
    partial_update=extend_schema(tags=["Books"]),
    destroy=extend_schema(tags=["Books"]),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").prefetch_related(
        "bookcategory_set__category"
    ).order_by("id")
    serializer_class = BookSerializer

    @action(detail=True, methods=["post"])
    def add_category(self, request, pk=None):
        book = self.get_object()
        name = request.data.get("name")
        priority = request.data.get("priority", 1)

        if not name:
            return Response({"error": "name is required"}, status=400)

        category, _ = Category.objects.get_or_create(name=name)
        obj, created = BookCategory.objects.get_or_create(
            book=book,
            category=category,
            defaults={"priority": priority},
        )
        if not created:
            obj.priority = priority
            obj.save(update_fields=["priority"])

        return Response({"status": "ok"})
    
@extend_schema_view(
    list=extend_schema(tags=["Book Categories"]),
    retrieve=extend_schema(tags=["Book Categories"]),
    create=extend_schema(tags=["Book Categories"]),
    update=extend_schema(tags=["Book Categories"]),
    partial_update=extend_schema(tags=["Book Categories"]),
    destroy=extend_schema(tags=["Book Categories"]),
)
class BookCategoryViewSet(viewsets.ModelViewSet):
    queryset = BookCategory.objects.select_related("book", "category").order_by("id")
    serializer_class = BookCategorySerializer
