# Generated by Django 5.1.4 on 2025-04-05 04:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0020_remove_policydocumentation_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='manual',
            name='send_email_to_approved_by',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='manual',
            name='send_email_to_checked_by',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='manual',
            name='send_notification_to_approved_by',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='manual',
            name='send_notification_to_checked_by',
            field=models.BooleanField(default=False),
        ),
    ]
