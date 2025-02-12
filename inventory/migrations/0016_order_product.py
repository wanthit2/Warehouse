# Generated by Django 5.0.6 on 2025-02-12 15:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0015_remove_profile_user_remove_customuser_stores_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="inventory.product",
            ),
        ),
    ]
