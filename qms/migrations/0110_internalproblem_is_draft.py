# Generated by Django 5.1.4 on 2025-04-26 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0109_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='internalproblem',
            name='is_draft',
            field=models.BooleanField(default=False),
        ),
    ]
