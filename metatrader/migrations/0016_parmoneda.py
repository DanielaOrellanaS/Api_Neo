# Generated by Django 4.1.1 on 2023-11-30 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0015_remove_events_id_alter_events_orden'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParMoneda',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('par', models.CharField(db_column='par', max_length=40)),
                ('moneda', models.CharField(db_column='moneda', max_length=40)),
            ],
            options={
                'db_table': 'par_moneda',
            },
        ),
    ]