# Generated by Django 5.2 on 2025-05-03 04:22

import django.db.models.deletion
import qms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('company', '0027_delete_customersatisfaction_delete_question'),
        ('qms', '0132_employeetrainingevaluation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReplayMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, max_length=255, null=True, storage=qms.models.MediaStorage(), upload_to=qms.models.generate_unique_filename)),
                ('message', models.TextField(blank=True, null=True)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_com', to='accounts.company')),
                ('from_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_users', to='company.users')),
                ('to_users', models.ManyToManyField(blank=True, related_name='received_replay_messages', to='company.users')),
            ],
        ),
    ]
