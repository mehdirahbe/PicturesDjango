# Generated by Django 5.1 on 2024-08-13 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PicturesApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photomodel',
            name='boite',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='photomodel',
            name='numero',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='photomodel',
            name='rangee',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='photomodel',
            name='troisieme_niveau',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
