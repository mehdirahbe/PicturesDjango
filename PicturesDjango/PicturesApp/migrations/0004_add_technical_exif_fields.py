# Generated manually after adding technical EXIF fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PicturesApp', '0003_photomodel_latitude_photomodel_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='photomodel',
            name='appareil',
            field=models.CharField(blank=True, db_index=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='photomodel',
            name='focale',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='photomodel',
            name='diaphragme',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='photomodel',
            name='temps_pose',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='photomodel',
            name='iso',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
