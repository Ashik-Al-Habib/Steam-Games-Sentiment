from django.contrib import admin
from .models import ProductReview


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('sentiment', 'app_id', 'app_name', 'review_text', 'genre', 'cleaned_review')
    search_fields = ('app_id', 'app_name', 'genre')
