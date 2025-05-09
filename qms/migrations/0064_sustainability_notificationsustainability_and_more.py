# Generated by Django 5.1.4 on 2025-04-17 04:35

import django.db.models.deletion
import qms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('company', '0012_alter_users_status'),
        ('qms', '0063_notificationchanges'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sustainability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(blank=True, choices=[('Legal', 'Legal'), ('Business', 'Business'), ('Client', 'Client'), ('Process/Specification', 'Process/Specification')], max_length=255, null=True)),
                ('no', models.CharField(blank=True, max_length=50, null=True)),
                ('review_frequency_year', models.TextField(blank=True, null=True)),
                ('review_frequency_month', models.TextField(blank=True, null=True)),
                ('upload_attachment', models.FileField(blank=True, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename_audit)),
                ('title', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('rivision', models.CharField(blank=True, max_length=50, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending for Review/Checking', 'Pending for Review/Checking'), ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'), ('Pending for Publish', 'Pending for Publish'), ('Correction Requested', 'Correction Requested'), ('Published', 'Published')], default='Pending for Review/Checking', max_length=50)),
                ('written_at', models.DateTimeField(blank=True, null=True)),
                ('checked_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('is_draft', models.BooleanField(default=False)),
                ('send_notification_to_checked_by', models.BooleanField(default=False)),
                ('send_email_to_checked_by', models.BooleanField(default=False)),
                ('send_notification_to_approved_by', models.BooleanField(default=False)),
                ('send_email_to_approved_by', models.BooleanField(default=False)),
                ('send_notification', models.BooleanField(default=False)),
                ('related_record_format', models.CharField(blank=True, max_length=50, null=True)),
                ('remarks', models.CharField(blank=True, max_length=50, null=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_sustain', to='company.users')),
                ('checked_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_sustain', to='company.users')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sustain', to='accounts.company')),
                ('published_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='published_ustainability', to='company.users')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sustain', to='company.users')),
                ('written_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='written_sustain', to='company.users')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationSustainability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, null=True)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sustainability', to='company.users')),
                ('sustainability', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qms.sustainability')),
            ],
        ),
        migrations.CreateModel(
            name='CorrectionSustainability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correction', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='corrections_from_sustainability', to='company.users')),
                ('to_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='corrections_to_sustainability', to='company.users')),
                ('sustainability', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qms.sustainability')),
            ],
        ),
    ]
