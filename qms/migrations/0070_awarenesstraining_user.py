# Generated by Django 5.1.4 on 2025-04-18 05:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0013_delete_awarenesstraining_and_more'),
        ('qms', '0069_remove_awarenesstraining_is_draft_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='awarenesstraining',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='awareness', to='company.users'),
        ),
    ]
