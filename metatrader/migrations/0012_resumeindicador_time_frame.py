# Generated by Django 4.1.1 on 2023-11-06 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0011_rename_par_id_resumeindicador_par'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumeindicador',
            name='time_frame',
            field=models.IntegerField(blank=True, db_column='time_frame', null=True),
        ),
    ]
