# Generated by Django 5.0.6 on 2025-02-10 11:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0013_supplier"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(2025, 2, 10, 18, 58, 32, 564174),
            ),
            preserve_default=False,
        ),
    ]
