# Generated by Django 5.1.4 on 2024-12-31 05:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0021_remove_audit_audit_from_internal_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='audit_from_internal',
            field=models.ManyToManyField(blank=True, null=True, related_name='users', to='company.users'),
        ),
    ]
