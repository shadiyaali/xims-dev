# Generated by Django 5.1.4 on 2024-12-31 06:11

import company.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0023_alter_audit_audit_from_internal'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inspection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('inspector_from', models.CharField(blank=True, max_length=50, null=True)),
                ('area', models.CharField(blank=True, max_length=50, null=True)),
                ('proposed_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('certification_body', models.CharField(blank=True, max_length=50, null=True)),
                ('inspector_type', models.CharField(blank=True, max_length=50, null=True)),
                ('procedures', models.CharField(blank=True, choices=[('Test', 'Test')], max_length=255, null=True)),
                ('date_conducted', models.DateField(blank=True, null=True)),
                ('upload_audit_report', models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit)),
                ('upload_non_coformities_report', models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit)),
                ('inspector_from_internal', models.ManyToManyField(blank=True, related_name='inspector_users', to='company.users')),
            ],
        ),
    ]
