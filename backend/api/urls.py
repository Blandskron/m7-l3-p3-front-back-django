from django.urls import path, include

urlpatterns = [
    path("", include("authors.urls")),
    path("", include("books.urls")),
    path("", include("categories.urls")),
    path("", include("profiles.urls")),
]
