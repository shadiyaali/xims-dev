# Generated by Django 5.1.4 on 2025-04-17 05:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('company', '0012_alter_users_status'),
        ('qms', '0064_sustainability_notificationsustainability_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Sustainability',
            new_name='Sustainabilities',
        ),
    ]
