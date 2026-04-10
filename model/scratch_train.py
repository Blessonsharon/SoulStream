import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from dataset_builder import CSV_PATH

print("Reading dataset...")
df = pd.read_csv(CSV_PATH).dropna()
texts = df['text'].tolist()
labels = df['label'].tolist()

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.10, random_state=42)

pipelines = [
    ("LR + Ngrams", make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(C=10, max_iter=1000))),
    ("LinearSVC + Ngrams", make_pipeline(TfidfVectorizer(ngram_range=(1, 3)), LinearSVC(C=1.0))),
    ("MLP + Ngrams", make_pipeline(TfidfVectorizer(), MLPClassifier(hidden_layer_sizes=(50,), max_iter=20)))
]

for name, model in pipelines:
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"{name} -> {acc * 100:.2f}%")
