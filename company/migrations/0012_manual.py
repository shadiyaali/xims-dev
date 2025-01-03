# Generated by Django 5.1.4 on 2025-01-02 09:14

import company.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0011_conformitycause_conformity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.CharField(blank=True, max_length=50, null=True)),
                ('document_type', models.CharField(blank=True, choices=[('System', 'System'), ('Paper', 'Paper'), ('External', 'External'), ('Work Instruction', 'Work Instruction')], max_length=255, null=True)),
                ('upload_attachment', models.FileField(blank=True, null=True, storage=company.models.MediaStorage(), upload_to=company.models.generate_unique_filename_audit)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('rivision', models.CharField(blank=True, max_length=50, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('send_notification', models.BooleanField(default=False)),
                ('publish', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_manual', to='company.users')),
                ('checked_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_manual', to='company.users')),
                ('written_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='written_manual', to='company.users')),
            ],
        ),
    ]
