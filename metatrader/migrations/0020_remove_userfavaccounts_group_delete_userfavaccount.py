# Generated by Django 4.1.1 on 2023-12-12 11:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0019_userfavaccounts_delete_userfavaccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfavaccounts',
            name='group',
        ),
    ]