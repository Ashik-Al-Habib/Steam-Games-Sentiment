import csv
import os
from django.core.management.base import BaseCommand
from SteamGameSentiment.models import ProductReview
from django.db import transaction


class Command(BaseCommand):
    help = 'Load data from CSV file into the ProductReview model'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        if not os.path.exists(csv_file_path):
            self.stderr.write(self.style.ERROR(f'File does not exist: {csv_file_path}'))
            return

        self.stdout.write(f'Starting to load data from {csv_file_path}')

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                batch_size = 1000
                batch = []
                row_count = 0

                for row in reader:
                    batch.append(ProductReview(
                        app_id=row['app_id'],
                        app_name=row['app_name'],
                        review_text=row['review_text'],
                        cleaned_review=row['cleaned_review'],
                        sentiment=row['sentiment'],
                        genre=row['genre']
                    ))

                    if len(batch) >= batch_size:
                        ProductReview.objects.bulk_create(batch)
                        row_count += len(batch)
                        self.stdout.write(f'{row_count} rows processed...')
                        batch = []

                if batch:
                    ProductReview.objects.bulk_create(batch)
                    row_count += len(batch)
                    self.stdout.write(f'{row_count} rows processed...')

            self.stdout.write(self.style.SUCCESS(f'Finished loading data from {csv_file_path}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
