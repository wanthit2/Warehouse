# Generated by Django 5.0.6 on 2025-02-03 10:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0010_order_product_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
