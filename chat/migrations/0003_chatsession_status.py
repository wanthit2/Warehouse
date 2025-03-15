# Generated by Django 5.0.6 on 2025-03-08 09:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0002_chatsession_shop_message_image_alter_message_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatsession",
            name="status",
            field=models.CharField(
                choices=[
                    ("open", "เปิด"),
                    ("in_progress", "กำลังดำเนินการ"),
                    ("closed", "ปิดแล้ว"),
                ],
                default="open",
                max_length=20,
            ),
        ),
    ]
