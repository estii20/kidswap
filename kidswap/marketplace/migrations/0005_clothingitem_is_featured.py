# Generated by Django 5.2.1 on 2025-05-16 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0004_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='clothingitem',
            name='is_featured',
            field=models.BooleanField(default=False),
        ),
    ]
