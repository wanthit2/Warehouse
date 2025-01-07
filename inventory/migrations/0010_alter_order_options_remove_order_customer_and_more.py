# Generated by Django 5.0.6 on 2025-01-05 17:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0009_remove_order_destination_remove_order_items_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={},
        ),
        migrations.RemoveField(
            model_name="order",
            name="customer",
        ),
        migrations.RemoveField(
            model_name="order",
            name="is_cancelled",
        ),
        migrations.RemoveField(
            model_name="order",
            name="name",
        ),
        migrations.RemoveField(
            model_name="order",
            name="order_date",
        ),
        migrations.RemoveField(
            model_name="order",
            name="product_code",
        ),
        migrations.RemoveField(
            model_name="order",
            name="total",
        ),
        migrations.AddField(
            model_name="order",
            name="product_name",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="ชื่อสินค้า"
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="status",
            field=models.CharField(
                default="Pending", max_length=50, verbose_name="สถานะ"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_id",
            field=models.AutoField(
                primary_key=True, serialize=False, verbose_name="ลำดับ"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="price",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="ราคา"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="quantity",
            field=models.IntegerField(verbose_name="จำนวน"),
        ),
    ]
