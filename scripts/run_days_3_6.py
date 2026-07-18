"""Reproducible Day 3–6 cleaning, modeling, evaluation, and artifact runner."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.model import (
    build_models,
    build_tfidf_vectorizer,
    evaluate_model,
    save_artifacts,
    select_production_model,
)
from src.preprocessing import TextPreprocessor, clean_dataset


RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
VIS_DIR = ROOT / "visualizations"


def load_raw_dataset() -> pd.DataFrame:
    shards = sorted(RAW_DIR.glob("*.parquet"))
    if not shards:
        raise FileNotFoundError(f"No Parquet shards found in {RAW_DIR}")
    return pd.concat([pd.read_parquet(path) for path in shards], ignore_index=True)


def save_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def save_confusion_matrix(matrix: list[list[int]], path: Path) -> None:
    figure, axis = plt.subplots(figsize=(6, 5))
    image = axis.imshow(matrix, cmap="Blues")
    axis.set(
        xticks=[0, 1, 2],
        yticks=[0, 1, 2],
        xticklabels=["Safe", "Phishing", "Spam"],
        yticklabels=["Safe", "Phishing", "Spam"],
        xlabel="Predicted label",
        ylabel="True label",
        title="Final Model Confusion Matrix",
    )
    for row in range(3):
        for column in range(3):
            axis.text(column, row, matrix[row][column], ha="center", va="center")
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main() -> None:
    raw = load_raw_dataset()
    cleaned, cleaning_summary = clean_dataset(raw)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_parquet(PROCESSED_DIR / "cleaned_dataset.parquet", index=False)
    save_json(PROCESSED_DIR / "cleaning_summary.json", cleaning_summary.to_dict())

    development, _ = train_test_split(
        cleaned,
        train_size=min(60_000, len(cleaned)),
        stratify=cleaned["label"],
        random_state=42,
    )
    train, test = train_test_split(
        development,
        test_size=0.20,
        stratify=development["label"],
        random_state=42,
    )
    train = train.reset_index(drop=True)
    test = test.reset_index(drop=True)

    preprocessor = TextPreprocessor()
    train_text = preprocessor.transform(train["text"].tolist())
    test_text = preprocessor.transform(test["text"].tolist())
    vectorizer = build_tfidf_vectorizer()
    train_features = vectorizer.fit_transform(train_text)
    test_features = vectorizer.transform(test_text)

    results: dict[str, dict] = {}
    fitted_models = {}
    for name, model in build_models().items():
        model.fit(train_features, train["label"])
        results[name] = evaluate_model(model, test_features, test["label"])
        fitted_models[name] = model

    selected_name = select_production_model(results)
    selected_model = fitted_models[selected_name]
    artifact_paths = save_artifacts(
        model_name=selected_name,
        model=selected_model,
        vectorizer=vectorizer,
        preprocessor=preprocessor,
    )

    selected_result = results[selected_name]
    false_negative_rows = test.loc[
        (test["label"] == 1)
        & (pd.Series(selected_result["predictions"]) != 1)
    ].copy()
    false_negative_rows["predicted_label"] = [
        prediction
        for prediction, true_label in zip(
            selected_result["predictions"], test["label"].tolist()
        )
        if true_label == 1 and prediction != 1
    ]
    false_negative_rows["text_preview"] = false_negative_rows["text"].astype(str).str.slice(0, 500)
    false_negative_rows[["label", "predicted_label", "text_preview"]].to_csv(
        VIS_DIR / "phishing_false_negatives.csv", index=False
    )

    comparison = []
    for name, result in results.items():
        comparison.append(
            {
                "model": name,
                "accuracy": result["accuracy"],
                "macro_f1": result["macro_f1"],
                "weighted_f1": result["weighted_f1"],
                "phishing_precision": result["per_class"]["Phishing"]["precision"],
                "phishing_recall": result["per_class"]["Phishing"]["recall"],
                "phishing_f1": result["per_class"]["Phishing"]["f1"],
            }
        )
    VIS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(comparison).to_csv(VIS_DIR / "model_comparison.csv", index=False)
    save_json(
        VIS_DIR / "model_metrics.json",
        {
            "cleaning_summary": cleaning_summary.to_dict(),
            "development_rows": len(development),
            "train_rows": len(train),
            "test_rows": len(test),
            "train_class_counts": train["label"].value_counts().sort_index().to_dict(),
            "test_class_counts": test["label"].value_counts().sort_index().to_dict(),
            "tfidf_features": int(train_features.shape[1]),
            "models": results,
            "selected_model": selected_name,
            "phishing_false_negative_count": len(false_negative_rows),
            "artifact_paths": artifact_paths,
        },
    )
    save_confusion_matrix(
        selected_result["confusion_matrix"], VIS_DIR / "confusion_matrix.png"
    )

    pipeline = __import__("joblib").load(artifact_paths["pipeline"])
    manual_examples = [
        "URGENT: verify your bank account at https://secure-example.com/login.",
        "Congratulations, claim your free prize by replying now.",
        "Team meeting is scheduled for tomorrow at 10 AM in room 204.",
        "Your password expires today; confirm it at support@example.com.",
    ]
    manual_predictions = pipeline.predict(manual_examples).tolist()
    save_json(
        VIS_DIR / "manual_predictions.json",
        {
            "model": selected_name,
            "examples": [
                {"text": text, "predicted_label": int(label)}
                for text, label in zip(manual_examples, manual_predictions)
            ],
        },
    )

    print(json.dumps({
        "cleaning_summary": cleaning_summary.to_dict(),
        "development_rows": len(development),
        "train_rows": len(train),
        "test_rows": len(test),
        "tfidf_features": int(train_features.shape[1]),
        "model_comparison": comparison,
        "selected_model": selected_name,
        "phishing_false_negative_count": len(false_negative_rows),
        "manual_predictions": manual_predictions,
        "artifact_paths": artifact_paths,
    }, indent=2))


if __name__ == "__main__":
    main()
