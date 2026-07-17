from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("books", "0001_initial")]

    operations = [
        migrations.AlterUniqueTogether(name="bookcategory", unique_together=set()),
        migrations.AddConstraint(
            model_name="bookcategory",
            constraint=models.UniqueConstraint(
                fields=("book", "category"), name="unique_book_category"
            ),
        ),
    ]
