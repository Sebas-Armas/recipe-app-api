# Generated by Django 3.2.16 on 2022-10-17 00:43

import Core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Core', '0006_rename_ingrediente_receta_ingredientes'),
    ]

    operations = [
        migrations.AddField(
            model_name='receta',
            name='imagen',
            field=models.ImageField(null=True, upload_to=Core.models.receta_imagen_file_path),
        ),
    ]