# Generated by Django 5.1.4 on 2024-12-27 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0004_documentation'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Documentation',
            new_name='PolicyDocumentation',
        ),
    ]
