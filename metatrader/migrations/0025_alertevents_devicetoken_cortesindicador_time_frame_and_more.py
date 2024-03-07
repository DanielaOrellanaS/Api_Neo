# Generated by Django 4.1.1 on 2024-02-28 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0024_cortesindicador_delete_userfavaccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('par_name', models.CharField(blank=True, db_column='par', max_length=25, null=True)),
                ('currency', models.CharField(db_column='currency', max_length=40)),
                ('name', models.CharField(db_column='name', max_length=40)),
                ('fecha', models.DateField(blank=True, db_column='fecha', null=True)),
                ('pips_ant', models.FloatField(blank=True, db_column='pips_ant', null=True)),
                ('count_events', models.BigIntegerField(blank=True, db_column='count_events', null=True)),
                ('max_pips', models.FloatField(blank=True, db_column='max_pips', null=True)),
                ('prom_pips', models.FloatField(blank=True, db_column='prom_pips', null=True)),
                ('ult_event', models.DateField(blank=True, db_column='ult_event', null=True)),
                ('par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metatrader.pares')),
            ],
            options={
                'db_table': 'alert_events',
            },
        ),
        migrations.CreateModel(
            name='DeviceToken',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('user', models.CharField(max_length=255)),
                ('token', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'DeviceToken',
            },
        ),
    ]