# Generated by Django 5.1.4 on 2025-04-18 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0014_delete_training'),
        ('qms', '0078_alter_training_date_conducted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='training_attendees',
            field=models.ManyToManyField(blank=True, related_name='training_attendees', to='company.users'),
        ),
    ]
