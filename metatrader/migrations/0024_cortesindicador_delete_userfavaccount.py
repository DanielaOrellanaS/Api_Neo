# Generated by Django 4.1.1 on 2023-12-27 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0023_account_group_delete_userfavaccount'),
    ]

    operations = [
        migrations.CreateModel(
            name='CortesIndicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, db_column='Date', null=True)),
                ('corte_buy', models.FloatField(blank=True, db_column='corte_buy', null=True)),
                ('corte_sell', models.FloatField(blank=True, db_column='corte_sell', null=True)),
                ('par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='metatrader.pares')),
            ],
            options={
                'db_table': 'CortesIndicador',
            },
        ),
    ]