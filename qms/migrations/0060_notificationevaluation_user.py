# Generated by Django 5.1.4 on 2025-04-16 10:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0012_alter_users_status'),
        ('qms', '0059_correctionevaluation_notificationevaluation'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationevaluation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='company.users'),
        ),
    ]
