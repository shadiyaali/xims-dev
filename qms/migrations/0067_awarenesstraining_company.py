# Generated by Django 5.1.4 on 2025-04-18 04:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('qms', '0066_awarenesstraining'),
    ]

    operations = [
        migrations.AddField(
            model_name='awarenesstraining',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='awareness', to='accounts.company'),
        ),
    ]
