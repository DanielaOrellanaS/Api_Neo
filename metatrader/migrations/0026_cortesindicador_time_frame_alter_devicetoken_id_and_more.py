# Generated by Django 4.1.1 on 2024-02-29 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0025_alertevents_devicetoken_cortesindicador_time_frame_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicetoken',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
