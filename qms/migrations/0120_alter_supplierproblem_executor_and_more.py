# Generated by Django 5.2 on 2025-04-29 03:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0025_delete_supplierproblem'),
        ('qms', '0119_alter_supplierproblem_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplierproblem',
            name='executor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='company.users'),
        ),
        migrations.AlterField(
            model_name='supplierproblem',
            name='no_car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qms.carnumber'),
        ),
    ]
