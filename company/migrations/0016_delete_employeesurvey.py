# Generated by Django 5.1.4 on 2025-04-19 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0015_delete_employeeevaluation'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmployeeSurvey',
        ),
    ]
