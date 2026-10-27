"""ML model: TF-IDF (word + character n-grams) + Logistic Regression, one head per target."""
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from . import config


def _build() -> Pipeline:
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True, min_df=1)),
        # character n-grams make the model robust to typos
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=2)),
    ])
    return Pipeline([
        ("features", features),
        ("clf", LogisticRegression(max_iter=2000, C=10, class_weight="balanced")),
    ])


def train(train_csv=None, save=True) -> dict:
    train_csv = train_csv or (config.DATA_DIR / "train.csv")
    df = pd.read_csv(train_csv)
    models = {}
    for target in ("issue_type", "urgency"):
        pipe = _build()
        pipe.fit(df["text"], df[target])
        models[target] = pipe
    if save:
        config.MODEL_DIR.mkdir(exist_ok=True)
        joblib.dump(models, config.MODEL_PATH)
    return models


def load(auto_train=True) -> dict:
    if config.MODEL_PATH.exists():
        return joblib.load(config.MODEL_PATH)
    if auto_train:
        return train()
    raise FileNotFoundError(f"Model not found: {config.MODEL_PATH}. Run scripts/train.py")


def predict_with_confidence(models: dict, text: str) -> dict:
    out = {}
    for target, pipe in models.items():
        proba = pipe.predict_proba([text])[0]
        idx = proba.argmax()
        out[target] = (pipe.classes_[idx], float(proba[idx]))
    return out
