# Generated by Django 5.1 on 2024-08-16 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PicturesApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photomodel',
            name='commentaire',
            field=models.TextField(db_index=True),
        ),
        migrations.AlterField(
            model_name='photomodel',
            name='sujet_dias',
            field=models.TextField(db_index=True),
        ),
        migrations.AddIndex(
            model_name='photomodel',
            index=models.Index(fields=['sujet_dias', 'commentaire'], name='PicturesApp_sujet_d_6ddd5b_idx'),
        ),
    ]
