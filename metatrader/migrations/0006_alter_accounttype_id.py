# Generated by Django 4.1.1 on 2023-08-28 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0005_alter_datatrader1m_date_alter_datatrader1m_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttype',
            name='id',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]