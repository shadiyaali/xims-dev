# Generated by Django 5.1.4 on 2025-04-07 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qms', '0026_alter_manual_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='manual',
            name='publish',
            field=models.BooleanField(default=False),
        ),
    ]
