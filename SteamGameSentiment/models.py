from django.db import models


class ProductReview(models.Model):
    app_id = models.IntegerField()
    app_name = models.CharField(max_length=255)
    review_text = models.TextField()
    cleaned_review = models.TextField()
    sentiment = models.IntegerField()
    genre = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.app_name} - Sentiment: {self.sentiment}"
