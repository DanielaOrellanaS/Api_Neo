# Generated by Django 4.1.1 on 2023-12-12 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metatrader', '0020_remove_userfavaccounts_group_delete_userfavaccount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfavaccounts',
            name='accounts',
        ),
        migrations.AddField(
            model_name='userfavaccounts',
            name='accounts',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
