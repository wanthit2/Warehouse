# Generated by Django 5.0.6 on 2025-02-10 11:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "inventory",
            "0012_category_product_status_alter_product_stock_quantity_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Supplier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("contact_info", models.TextField()),
            ],
        ),
    ]
