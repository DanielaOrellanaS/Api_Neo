# Generated by Django 4.1.1 on 2023-12-12 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0018_remove_pips_fecha_num_pips_fecha_numero'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavAccounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=4)),
                ('group', models.IntegerField(blank=True, db_column='group', null=True)),
                ('accounts', models.ManyToManyField(related_name='favorite_accounts', to='metatrader.account')),
            ],
            options={
                'db_table': 'UserFavAccounts',
            },
        ),
    ]
