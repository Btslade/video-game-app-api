# Generated by Django 3.2.19 on 2023-06-02 16:11

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_rename_console_videogame_consoles'),
    ]

    operations = [
        migrations.AddField(
            model_name='videogame',
            name='image',
            field=models.ImageField(null=True, upload_to=core.models.videogame_image_file_path),
        ),
    ]