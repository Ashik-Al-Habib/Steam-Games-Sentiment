from django.shortcuts import render
from nltk.sentiment import SentimentIntensityAnalyzer
from .models import ProductReview
from django.http import JsonResponse
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import joblib
from .forms import ProductSearchForm
import nltk
import sklearn
from collections import Counter

nltk.download('punkt')

from django.shortcuts import render
from django.db.models import Count, Q
from .models import ProductReview
from .forms import ProductSearchForm


def search_product(request):
    # Fetch product IDs with total review count, good adj count, and bad adj count
    product_counts = ProductReview.objects.values('app_id', 'app_name', 'genre').annotate(
        total_reviews=Count('review_text'),
        good_count=Count('review_text', filter=Q(review_text__icontains='good')),
        bad_count=Count('review_text', filter=Q(review_text__icontains='bad'))
    ).filter(total_reviews__gte=500).order_by('-total_reviews')

    return render(request, 'SteamGameSentiment/search.html', {
        'product_counts': product_counts
    })


def analyze_product_reviews(app_id, algorithm):
    # Filter the reviews based on product ID
    reviews = ProductReview.objects.filter(app_id=app_id)
    if not reviews.exists():
        return {"error": f"No reviews found for Product ID: {app_id}"}

    # loading the model
    model_path = '/Users/ashikalhabib/Desktop/test/'
    model = joblib.load(model_path + f'{algorithm}.h5')

    # Dummy accuracy value; replace this with the actual method to get model accuracy
    accuracy = model.accuracy * 100

    # Convert to DataFrame
    reviews_df = pd.DataFrame(list(reviews.values()))

    # Concatenate all reviews into a single string
    reviews_text = ' '.join(reviews_df['review_text'].astype(str))
    # Tokenize and POS tag the text
    tokens = word_tokenize(reviews_text)
    pos_tags = pos_tag(tokens)
    # Filter out adjectives
    adjectives = [word for word, pos in pos_tags if pos in ['JJ', 'JJR', 'JJS']]
    # Filter out stop words from adjectives
    stop_words = set(stopwords.words('english'))
    adjectives = [adj for adj in adjectives if adj.lower() not in stop_words]
    if not adjectives:
        return {"error": f"No adjectives found in the reviews for product ID: {app_id}"}
    # Initialize SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    # Separate good and bad adjectives
    good_adjectives = []
    bad_adjectives = []
    for adj in adjectives:
        sentiment = sia.polarity_scores(adj)
        if sentiment['compound'] > 0:
            good_adjectives.append(adj)
        elif sentiment['compound'] < 0:
            bad_adjectives.append(adj)

    # Determine overall sentiment based on counts
    good_count = len(good_adjectives)
    bad_count = len(bad_adjectives)

    if good_count > bad_count:
        overall_sentiment = "Good"
    elif bad_count > good_count:
        overall_sentiment = "Bad"
    else:
        overall_sentiment = "Neutral"

    # Generate word clouds
    good_wordcloud_base64 = generate_word_cloud(good_adjectives, f"Good Adjectives for Product ID: {app_id}")
    bad_wordcloud_base64 = generate_word_cloud(bad_adjectives, f"Bad Adjectives for Product ID: {app_id}")

    # Extract top 4 words from good adjectives
    if good_count > bad_count:
        word_freq = Counter(good_adjectives)
        top_4_words = [word for word, freq in word_freq.most_common(4)]
    else:
        word_freq = Counter(bad_adjectives)
        top_4_words = [word for word, freq in word_freq.most_common(4)]

    # Define recommended games
    recommended_games = {
        2357570: {"app_id": 1172470, "app_name": "Apex Legends", "genre": "First-person shooter/Hero shooter"},
        1962660: {"app_id": 2000950, "app_name": "Call of Duty Modern Warfare", "genre": "First-person shooter"}
    }

    recommended_game = None
    if app_id in recommended_games and overall_sentiment == "Bad":
        recommended_game = recommended_games[app_id]

    return {
        'app_id': app_id,
        'app_name': reviews.first().app_name,
        'genre': reviews.first().genre,
        'good_adjectives_count': good_count,
        'bad_adjectives_count': bad_count,
        'overall_sentiment': overall_sentiment,
        'good_adjectives': good_adjectives,
        'bad_adjectives': bad_adjectives,
        'accuracy': accuracy,
        'good_wordcloud_base64': good_wordcloud_base64,
        'bad_wordcloud_base64': bad_wordcloud_base64,
        'top_4_words': top_4_words,
        'recommended_game': recommended_game
    }


def generate_word_cloud(words, title):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(words))
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


@csrf_exempt
def sentiment_analysis(request):
    form = ProductSearchForm()
    good_wordcloud_base64 = None
    bad_wordcloud_base64 = None
    result = None
    if request.method == 'POST':
        form = ProductSearchForm(request.POST)
        if form.is_valid():
            app_id = form.cleaned_data['app_id']
            algorithm = form.cleaned_data['algorithm']
            result = analyze_product_reviews(app_id, algorithm)

            if isinstance(result, dict):
                good_adjectives = result.get('good_adjectives', [])
                bad_adjectives = result.get('bad_adjectives', [])

                if good_adjectives:
                    good_wordcloud_base64 = generate_word_cloud(good_adjectives,
                                                                f"Good Adjectives for Game ID: {app_id}")
                if bad_adjectives:
                    bad_wordcloud_base64 = generate_word_cloud(bad_adjectives,
                                                               f"Bad Adjectives for Game ID: {app_id}")

    return render(request, 'SteamGameSentiment/sentiment.html', {
        'form': form,
        'result': result,
        'good_wordcloud_base64': good_wordcloud_base64,
        'bad_wordcloud_base64': bad_wordcloud_base64,
    })
