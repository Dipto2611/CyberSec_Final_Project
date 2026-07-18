"""Feature engineering, model training, evaluation, and artifact utilities for Days 4–6."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from .preprocessing import LABEL_NAMES, TextPreprocessor


def build_tfidf_vectorizer() -> TfidfVectorizer:
    """Create the single vectorizer configuration shared by all three models."""

    return TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.995,
        max_features=50_000,
        sublinear_tf=True,
        dtype=np.float32,
    )


def build_models() -> dict[str, Any]:
    """Build comparable classifiers using the same feature matrix and fixed seed."""

    return {
        "MultinomialNB": MultinomialNB(alpha=0.1),
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            solver="lbfgs",
            random_state=42,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=40,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=42,
        ),
    }


def split_stratified(
    dataframe: pd.DataFrame,
    *,
    label_column: str = "label",
    text_column: str = "text",
    test_size: float = 0.20,
    random_state: int = 42,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Return raw text/labels split with class proportions preserved."""

    from sklearn.model_selection import train_test_split

    train, test = train_test_split(
        dataframe[[text_column, label_column]],
        test_size=test_size,
        stratify=dataframe[label_column],
        random_state=random_state,
    )
    return train[text_column], test[text_column], train[label_column], test[label_column]


def evaluate_model(
    model: Any,
    features: Any,
    labels: pd.Series,
) -> dict[str, Any]:
    """Return accuracy, macro/weighted scores, per-class scores, and a confusion matrix."""

    predictions = model.predict(features)
    label_order = sorted(LABEL_NAMES)
    report = classification_report(
        labels,
        predictions,
        labels=label_order,
        target_names=[LABEL_NAMES[label] for label in label_order],
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(labels, predictions, labels=label_order)
    per_class = {
        LABEL_NAMES[label]: {
            "precision": float(report[LABEL_NAMES[label]]["precision"]),
            "recall": float(report[LABEL_NAMES[label]]["recall"]),
            "f1": float(report[LABEL_NAMES[label]]["f1-score"]),
            "support": int(report[LABEL_NAMES[label]]["support"]),
        }
        for label in label_order
    }
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(labels, predictions, average="weighted", zero_division=0)),
        "per_class": per_class,
        "confusion_matrix": matrix.tolist(),
        "predictions": predictions.tolist(),
    }


def select_production_model(results: dict[str, dict[str, Any]]) -> str:
    """Select by phishing F1 first, then macro F1 and accuracy as tie-breakers."""

    return max(
        results,
        key=lambda name: (
            results[name]["per_class"]["Phishing"]["f1"],
            results[name]["macro_f1"],
            results[name]["accuracy"],
        ),
    )


def save_artifacts(
    *,
    model_name: str,
    model: Any,
    vectorizer: TfidfVectorizer,
    preprocessor: TextPreprocessor,
    output_dir: str | Path | None = None,
) -> dict[str, str]:
    """Save standalone model/vectorizer and a complete inference pipeline."""

    # Always save relative to the project root unless explicitly overridden.
    if output_dir is None:
        output = Path(__file__).resolve().parents[1] / "models"
    else:
        output = Path(output_dir)
        if not output.is_absolute():
            output = Path(__file__).resolve().parents[1] / output

    output.mkdir(parents=True, exist_ok=True)

    model_path = output / "final_model.joblib"
    vectorizer_path = output / "tfidf_vectorizer.joblib"
    pipeline_path = output / "final_pipeline.joblib"
    metadata_path = output / "model_metadata.joblib"

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            ("tfidf", vectorizer),
            ("model", model),
        ]
    )
    joblib.dump(pipeline, pipeline_path)

    metadata = {
        "model_name": model_name,
        "label_mapping": {
            str(key): value for key, value in LABEL_NAMES.items()
        },
        "preprocessing": {
            "url_strategy": "urltoken plus domain components",
            "email_strategy": "emailtoken plus domain components",
            "number_strategy": "numtoken",
            "stemming": "Porter stemming",
        },
    }

    joblib.dump(metadata, metadata_path)

    return {
        "model": str(model_path),
        "vectorizer": str(vectorizer_path),
        "pipeline": str(pipeline_path),
        "metadata": str(metadata_path),
    }


def load_pipeline(path: str | Path | None = None) -> Pipeline:
    """Load the saved inference pipeline."""

    if path is None:
        path = Path(__file__).resolve().parents[1] / "models" / "final_pipeline.joblib"
    else:
        path = Path(path)
        if not path.is_absolute():
            path = Path(__file__).resolve().parents[1] / path

    return joblib.load(path)
