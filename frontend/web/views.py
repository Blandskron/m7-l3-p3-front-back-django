import os

import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import AuthorCreateForm, BookCreateForm

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1").rstrip("/")


def _extract_api_error(resp: requests.Response) -> str:
    """
    DRF suele responder errores como dict/list.
    Lo convertimos en texto legible para messages.error.
    """
    try:
        data = resp.json()
    except Exception:
        return resp.text

    # dict: {"field": ["msg1", "msg2"], "non_field_errors": ["..."]}
    if isinstance(data, dict):
        parts = []
        for k, v in data.items():
            if isinstance(v, list):
                parts.append(f"{k}: " + "; ".join(map(str, v)))
            else:
                parts.append(f"{k}: {v}")
        return " | ".join(parts)

    # list: ["error1", "error2"]
    if isinstance(data, list):
        return "; ".join(map(str, data))

    return str(data)


def _parse_categories_text(text: str):
    """
    Convierte: "Novela:1, Historia:2, Ciencia"
    En: [{"name":"Novela","priority":1}, {"name":"Historia","priority":2}, {"name":"Ciencia","priority":1}]
    """
    out = []
    if not text:
        return out

    chunks = [c.strip() for c in text.split(",") if c.strip()]
    for ch in chunks:
        if ":" in ch:
            name, pr = ch.split(":", 1)
            name = name.strip()
            pr = pr.strip()
            if not name:
                continue
            try:
                priority = int(pr) if pr else 1
            except ValueError:
                priority = 1
            out.append({"name": name, "priority": max(priority, 1)})
        else:
            out.append({"name": ch.strip(), "priority": 1})

    # eliminar duplicadas por nombre (manteniendo la mayor prioridad)
    dedup = {}
    for item in out:
        key = item["name"].lower()
        if key not in dedup or item["priority"] > dedup[key]["priority"]:
            dedup[key] = item
    return list(dedup.values())


def books_list(request):
    books = []
    error = None

    try:
        r = requests.get(f"{API_BASE}/books/", timeout=10)
        r.raise_for_status()
        books = r.json()
    except Exception as e:
        error = f"No pude cargar libros desde la API: {e}"

    return render(request, "web/books_list.html", {"books": books, "error": error})


def author_create(request):
    if request.method == "POST":
        form = AuthorCreateForm(request.POST)
        if form.is_valid():
            payload = {"name": form.cleaned_data["name"]}
            bd = form.cleaned_data.get("birth_date")
            if bd:
                payload["birth_date"] = bd.isoformat()

            try:
                r = requests.post(f"{API_BASE}/authors/", json=payload, timeout=10)
                if r.status_code >= 400:
                    messages.error(request, f"Error API al crear autor: {_extract_api_error(r)}")
                else:
                    messages.success(request, "Autor creado correctamente.")
                    return redirect("books_list")
            except Exception as e:
                messages.error(request, f"Error conectando con API: {e}")
    else:
        form = AuthorCreateForm()

    return render(request, "web/author_create.html", {"form": form})


def book_create(request):
    # 1) cargar autores para el select
    authors_choices = []
    try:
        ar = requests.get(f"{API_BASE}/authors/", timeout=10)
        ar.raise_for_status()
        authors = ar.json()
        authors_choices = [(str(a["id"]), a["name"]) for a in authors]
    except Exception:
        authors_choices = []

    if request.method == "POST":
        form = BookCreateForm(request.POST)
        form.fields["author_id"].choices = authors_choices

        if form.is_valid():
            categories_input = _parse_categories_text(form.cleaned_data.get("categories_input_text", ""))

            payload = {
                "title": form.cleaned_data["title"],
                "isbn": form.cleaned_data["isbn"],
                "author_id": int(form.cleaned_data["author_id"]),
            }

            pd = form.cleaned_data.get("published_date")
            if pd:
                payload["published_date"] = pd.isoformat()

            # IMPORTANT: el serializer espera categories_input, no "categories"
            if categories_input:
                payload["categories_input"] = categories_input

            try:
                r = requests.post(f"{API_BASE}/books/", json=payload, timeout=10)
                if r.status_code >= 400:
                    messages.error(request, f"Error API al crear libro: {_extract_api_error(r)}")
                else:
                    messages.success(request, "Libro creado correctamente.")
                    return redirect("books_list")
            except Exception as e:
                messages.error(request, f"Error conectando con API: {e}")
    else:
        form = BookCreateForm()
        form.fields["author_id"].choices = authors_choices

        if not authors_choices:
            messages.warning(request, "No hay autores disponibles. Crea un autor primero.")

    return render(request, "web/book_create.html", {"form": form})
