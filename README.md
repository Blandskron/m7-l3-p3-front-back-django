# Biblioteca educativa con Django ORM

Proyecto didáctico compuesto por una API REST (backend) y una interfaz web Django
(frontend). Permite administrar autores, libros, categorías y socios, y muestra de
forma directa las tres relaciones principales del ORM de Django.

## Ejecución con Docker

El único requisito es Docker. Desde la raíz del repositorio:

```bash
docker compose up --build
```

Si esos puertos ya están ocupados, se pueden cambiar sin editar archivos:
`BACKEND_PORT=18000 FRONTEND_PORT=18001 docker compose up --build` (en
PowerShell, definir ambas variables con `$env:` antes del comando).

- Interfaz web: http://localhost:8001/
- API y Swagger: http://localhost:8000/ y http://localhost:8000/docs/swagger/
- Administración: http://localhost:8000/admin/
- Usuario administrador: `admin`
- Contraseña: `admin1234`

El arranque aplica migraciones, crea o actualiza el superusuario y carga datos de
demostración. Estas acciones son idempotentes, por lo que reiniciar los contenedores
no duplica información ni genera errores. SQLite se guarda en el volumen Docker
`library_data`.

Para detener el proyecto:

```bash
docker compose down
```

## Relaciones educativas

### Uno a uno: usuario y perfil de socio

`MemberProfile.user` usa `OneToOneField`. Se emplea porque cada usuario sólo puede
tener un perfil de socio y cada perfil pertenece a un único usuario. Puede verse en
el admin o en `GET /api/v1/profiles/`. El acceso inverso es
`user.member_profile`. Al borrar el usuario, `on_delete=models.CASCADE` elimina su
perfil.

### Muchos a uno: libros y autor

`Book.author` usa `ForeignKey`: un autor puede escribir muchos libros, mientras que
cada libro tiene un autor. Se implementa con `related_name="books"`, por lo que los
libros se consultan mediante `author.books.all()`. El borrado en cascada elimina los
libros cuando se elimina su autor; esta decisión resulta fácil de demostrar en las
pruebas educativas.

### Muchos a muchos: libros y categorías

`Book.categories` usa `ManyToManyField`: un libro puede pertenecer a varias
categorías y una categoría puede contener varios libros. La entidad intermedia
explícita `BookCategory` agrega los campos `priority` y `assigned_at`, y evita
asignaciones duplicadas mediante `UniqueConstraint`. Puede gestionarse desde el
formulario web, el admin o `/api/v1/book-categories/`.

## API principal

| Método | Ruta | Uso |
|---|---|---|
| GET/POST | `/api/v1/authors/` | Autores |
| GET/POST | `/api/v1/books/` | Libros y categorías de entrada |
| GET/POST | `/api/v1/categories/` | Categorías |
| GET/POST | `/api/v1/book-categories/` | Entidad intermedia |
| GET/POST | `/api/v1/profiles/` | Relación usuario-perfil |

## Ejecución local opcional

Con Python 3.14 y las dependencias instaladas:

```bash
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

En otra terminal:

```bash
cd frontend
python manage.py migrate
python manage.py runserver 8001
```

## Pruebas y verificaciones

```bash
cd backend
python manage.py check
python manage.py migrate
python manage.py test

cd ../frontend
python manage.py check
python manage.py migrate
python manage.py test

cd ..
docker compose config
docker compose build
docker compose up
```

Las pruebas cubren la unicidad uno-a-uno, la relación inversa y el borrado en
cascada muchos-a-uno, la entidad intermedia muchos-a-muchos, creación mediante API,
rutas principales y consumo desde la interfaz web.
