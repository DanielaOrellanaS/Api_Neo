# Generated by Django 4.1.1 on 2023-08-23 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0004_datatrader1m'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datatrader1m',
            name='date',
            field=models.DateField(blank=True, db_column='Date', null=True),
        ),
        migrations.AlterField(
            model_name='datatrader1m',
            name='time',
            field=models.TimeField(blank=True, db_column='Time', null=True),
        ),
    ]
