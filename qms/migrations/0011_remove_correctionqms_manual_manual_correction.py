# Generated by Django 5.1.4 on 2025-03-26 09:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0010_alter_manual_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correctionqms',
            name='manual',
        ),
        migrations.AddField(
            model_name='manual',
            name='correction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qms.correctionqms'),
        ),
    ]
