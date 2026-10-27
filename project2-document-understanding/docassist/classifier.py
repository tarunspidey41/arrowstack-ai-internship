"""Document-type classifier: TF-IDF + Logistic Regression (invoice / PO / service agreement / other)."""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from . import config, synth


def train(save=True, n_per_class=150, seed=1):
    texts, labels = synth.training_corpus(n_per_class, seed)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True)),
        ("clf", LogisticRegression(max_iter=2000, C=10, class_weight="balanced")),
    ])
    pipe.fit(texts, labels)
    if save:
        config.MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(pipe, config.MODEL_PATH)
    return pipe


def load():
    if config.MODEL_PATH.exists():
        return joblib.load(config.MODEL_PATH)
    return train()


def predict(pipe, text: str):
    proba = pipe.predict_proba([text])[0]
    i = proba.argmax()
    return pipe.classes_[i], float(proba[i])


# Keyword baseline: first matching keyword wins (deliberately naive)
def baseline_predict(text: str) -> str:
    t = text.lower()
    if "agreement" in t or "contract" in t:
        return "service_agreement"
    if "purchase order" in t:
        return "purchase_order"
    if "invoice" in t:
        return "invoice"
    return "other"
