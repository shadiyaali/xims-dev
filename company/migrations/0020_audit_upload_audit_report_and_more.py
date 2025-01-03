# Generated by Django 5.1.4 on 2024-12-31 05:44

import company.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0019_alter_carnumber_root_cause_audit'),
    ]

    operations = [
        migrations.AddField(
            model_name='audit',
            name='upload_audit_report',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit),
        ),
        migrations.AddField(
            model_name='audit',
            name='upload_non_coformities_report',
            field=models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit),
        ),
    ]
