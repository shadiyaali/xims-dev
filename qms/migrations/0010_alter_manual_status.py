# Generated by Django 5.1.4 on 2025-03-26 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0009_alter_correctionqms_from_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manual',
            name='status',
            field=models.CharField(choices=[('Pending for Review/Checking', 'Pending for Review/Checking'), ('Reviewed,Pending for Approval', 'Reviewed,Pending for Approval'), ('Approved', 'Approved'), ('Correcton Requested', 'Correcton Requested')], default='Pending for Review/Checking', max_length=50),
        ),
    ]
