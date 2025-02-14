# Generated by Django 5.0.7 on 2024-07-18 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProductReview",
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
                ("app_id", models.IntegerField()),
                ("app_name", models.CharField(max_length=255)),
                ("review_text", models.TextField()),
                ("cleaned_review", models.TextField()),
                ("sentiment", models.IntegerField()),
                ("genre", models.CharField(max_length=255)),
            ],
        ),
    ]
