from django import forms

ALGORITHMS = [
    ('random_forest_model', 'Random Forest'),
    ('naive_bayes_model', 'Naive Bayes'),
    ('svm_model', 'SVM'),
    ('xg_boost_model', 'XGBoost'),
]


class ProductSearchForm(forms.Form):
    app_id = forms.CharField(label='Enter Game ID', max_length=100)
    # product_id = forms.ChoiceField(choices=PRODUCT_IDS, label='Choose Product ID')
    algorithm = forms.ChoiceField(choices=ALGORITHMS, label='Choose Algorithm')
