#!/bin/sh
set -eu

SERVICE="${SERVICE:-backend}"

if [ "$SERVICE" = "backend" ]; then
    cd /app/backend
    python manage.py migrate --noinput
    python manage.py shell -c "from django.contrib.auth import get_user_model; import os; U=get_user_model(); username=os.environ.get('DJANGO_SUPERUSER_USERNAME','admin'); email=os.environ.get('DJANGO_SUPERUSER_EMAIL','admin@example.com'); password=os.environ.get('DJANGO_SUPERUSER_PASSWORD','admin1234'); user, created=U.objects.get_or_create(username=username, defaults={'email': email, 'is_staff': True, 'is_superuser': True}); user.is_staff=True; user.is_superuser=True; user.email=email; user.set_password(password); user.save()"
    python manage.py seed_demo
    exec python manage.py runserver 0.0.0.0:8000
fi

if [ "$SERVICE" = "frontend" ]; then
    cd /app/frontend
    python manage.py migrate --noinput
    exec python manage.py runserver 0.0.0.0:8001
fi

echo "SERVICE debe ser 'backend' o 'frontend'." >&2
exit 1
