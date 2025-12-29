# Generated manually to increase image_url max_length

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flowers", "0003_favorite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flower",
            name="image_url",
            field=models.URLField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name="Изображение (URL)",
            ),
        ),
    ]

