# Generated by Django 3.1 on 2021-01-24 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema', '0002_rename_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filmwork',
            name='imdb_pconst',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='imdb parrent'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='imdb_tconst',
            field=models.CharField(max_length=255, verbose_name='imdb id'),
        ),
    ]
