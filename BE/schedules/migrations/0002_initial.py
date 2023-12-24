# Generated by Django 4.0.3 on 2023-12-24 04:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schedules', '0001_initial'),
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='team',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='schedule', to='teams.team'),
        ),
    ]
