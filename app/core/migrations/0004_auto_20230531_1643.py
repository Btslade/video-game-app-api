# Generated by Django 3.2.19 on 2023-05-31 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20230506_2117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videogame',
            name='system',
        ),
        migrations.CreateModel(
            name='Console',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('rating', models.DecimalField(decimal_places=2, max_digits=4)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='videogame',
            name='console',
            field=models.ManyToManyField(to='core.Console'),
        ),
    ]
