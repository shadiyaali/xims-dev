 
# Generated by Django 5.1.4 on 2024-12-27 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_outstandingtoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, null=True, unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('confirm_password', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=255)),
                ('date_of_birth', models.DateField()),
                ('address', models.TextField()),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('zip_po_box', models.CharField(blank=True, max_length=20, null=True)),
                ('province_state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(default=True, max_length=50, null=True)),
                ('department_division', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('confirm_email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('office_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('mobile_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('fax', models.CharField(blank=True, max_length=15, null=True)),
                ('secret_question', models.CharField(max_length=100)),
                ('answer', models.CharField(max_length=100)),
                ('notes', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('live', 'live'), ('blocked', 'Blocked')], default='live', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='OutstandingToken',
        ),
    ]
 
 
