from django.db import transaction
from rest_framework import serializers
from .models import Book, BookCategory
from categories.models import Category
from authors.models import Author
from authors.serializers import AuthorSerializer
from categories.serializers import CategorySerializer


class BookCategoryWriteSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    priority = serializers.IntegerField(min_value=1, required=False, default=1)


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        source="author",
        queryset=Author.objects.all(),
        write_only=True,
    )
    category_assignments = serializers.SerializerMethodField()
    categories_input = BookCategoryWriteSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "isbn",
            "published_date",
            "author",
            "author_id",
            "category_assignments",
            "categories_input",
        ]

    def get_category_assignments(self, obj):
        assignments = obj.bookcategory_set.select_related("category")
        return BookCategorySerializer(assignments, many=True).data

    @transaction.atomic
    def create(self, validated_data):
        categories_payload = validated_data.pop("categories_input", [])
        book = Book.objects.create(**validated_data)

        for item in categories_payload:
            category, _ = Category.objects.get_or_create(name=item["name"])
            BookCategory.objects.update_or_create(
                book=book,
                category=category,
                defaults={"priority": item.get("priority", 1)},
            )

        return book

    @transaction.atomic
    def update(self, instance, validated_data):
        categories_payload = validated_data.pop("categories_input", None)
        instance = super().update(instance, validated_data)
        if categories_payload is not None:
            instance.bookcategory_set.all().delete()
            for item in categories_payload:
                category, _ = Category.objects.get_or_create(name=item["name"])
                BookCategory.objects.create(
                    book=instance,
                    category=category,
                    priority=item.get("priority", 1),
                )
        return instance
    

class BookCategorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = BookCategory
        fields = [
            "id",
            "book",
            "category",
            "book_title",
            "category_name",
            "priority",
            "assigned_at",
        ]
