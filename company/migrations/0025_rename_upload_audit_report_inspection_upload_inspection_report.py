# Generated by Django 5.1.4 on 2024-12-31 06:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0024_inspection'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inspection',
            old_name='upload_audit_report',
            new_name='upload_inspection_report',
        ),
    ]