"""Reusable data cleaning and NLP text preprocessing components.

The transformer in this module is deliberately deterministic and sklearn-compatible.  It
normalizes security-relevant structures (URLs, email addresses, and numbers) into explicit
tokens before punctuation and stop-word handling, so training and inference use the same logic.
"""

from __future__ import annotations

import html
import math
import re
import unicodedata
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from typing import Iterable, Sequence
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from nltk.stem import PorterStemmer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


LABEL_VALUES = frozenset({0, 1, 2})
LABEL_NAMES = {0: "Safe", 1: "Phishing", 2: "Spam"}

URL_PATTERN = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>]+")
EMAIL_PATTERN = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
NUMBER_PATTERN = re.compile(r"(?<![A-Za-z])\d+(?:[.,:/-]\d+)*(?![A-Za-z])")


class _HTMLTextExtractor(HTMLParser):
    """Small dependency-free HTML-to-text adapter for malformed email HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def text(self) -> str:
        return " ".join(self.parts)


def strip_html(value: str) -> str:
    """Remove markup while retaining visible text, with a regex fallback."""

    parser = _HTMLTextExtractor()
    try:
        parser.feed(value)
        parser.close()
        return parser.text()
    except Exception:
        return re.sub(r"<[^>]*>", " ", value)


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, (float, np.floating)):
        return math.isnan(float(value))
    return False


def _domain_tokens(value: str) -> str:
    """Extract domain components without retaining punctuation-heavy raw URLs."""

    candidate = value if re.match(r"(?i)^https?://", value) else f"http://{value}"
    parsed = urlparse(candidate)
    domain = parsed.netloc or parsed.path.split("/", 1)[0]
    domain = re.sub(r"^www\.", "", domain, flags=re.IGNORECASE)
    parts = re.findall(r"[A-Za-z0-9]+", domain.casefold())
    return " ".join(parts)


def _replace_email(match: re.Match[str]) -> str:
    address = match.group(0)
    domain = address.rsplit("@", 1)[-1]
    domain_parts = re.findall(r"[A-Za-z0-9]+", domain.casefold())
    return " emailtoken " + " ".join(domain_parts)


def _replace_url(match: re.Match[str]) -> str:
    raw_url = match.group(0).rstrip(".,;:!?)]}")
    domain = _domain_tokens(raw_url)
    return " urltoken urldomain " + domain


def remove_punctuation(value: str) -> str:
    """Remove Unicode punctuation/symbols while retaining letters and combining marks."""

    characters = []
    for character in value:
        category = unicodedata.category(character)
        if character == "_" or category.startswith(("P", "S")):
            characters.append(" ")
        else:
            characters.append(character)
    return "".join(characters)


@dataclass(frozen=True)
class CleaningSummary:
    """Auditable counts produced by :func:`clean_dataset`."""

    input_rows: int
    missing_text_rows: int
    whitespace_only_rows: int
    invalid_label_rows: int
    duplicate_rows_removed: int
    output_rows: int
    output_class_counts: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def validate_labels(dataframe: pd.DataFrame, label_column: str = "label") -> None:
    """Validate that labels are complete and belong to the locked three-class set."""

    if label_column not in dataframe.columns:
        raise ValueError(f"Missing required label column: {label_column}")
    numeric = pd.to_numeric(dataframe[label_column], errors="coerce")
    invalid_mask = numeric.isna() | ~numeric.isin(LABEL_VALUES)
    if bool(invalid_mask.any()):
        raise ValueError(
            f"Found {int(invalid_mask.sum())} invalid labels; expected only {sorted(LABEL_VALUES)}"
        )


def clean_dataset(
    dataframe: pd.DataFrame,
    *,
    label_column: str = "label",
    text_column: str = "text",
) -> tuple[pd.DataFrame, CleaningSummary]:
    """Clean only unusable rows and exact duplicate records.

    Raw data is never mutated. Missing and whitespace-only texts are excluded because they cannot
    provide a learnable message. Exact duplicates are removed after that exclusion, preserving
    the first occurrence and all native numeric labels.
    """

    required = {label_column, text_column}
    missing_columns = required.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
    validate_labels(dataframe, label_column)

    result = dataframe[[label_column, text_column]].copy()
    input_rows = len(result)
    missing_mask = result[text_column].isna()
    text_as_string = result[text_column].astype("string")
    whitespace_mask = (~missing_mask) & text_as_string.str.strip().eq("")
    invalid_label_rows = int(
        pd.to_numeric(result[label_column], errors="coerce").isna().sum()
    )

    usable = result.loc[~missing_mask & ~whitespace_mask].copy()
    duplicate_mask = usable.duplicated(subset=[label_column, text_column], keep="first")
    duplicate_rows_removed = int(duplicate_mask.sum())
    usable = usable.loc[~duplicate_mask].reset_index(drop=True)

    counts = usable[label_column].value_counts().sort_index().to_dict()
    summary = CleaningSummary(
        input_rows=input_rows,
        missing_text_rows=int(missing_mask.sum()),
        whitespace_only_rows=int(whitespace_mask.sum()),
        invalid_label_rows=invalid_label_rows,
        duplicate_rows_removed=duplicate_rows_removed,
        output_rows=len(usable),
        output_class_counts={str(int(label)): int(count) for label, count in counts.items()},
    )
    return usable, summary


class TextPreprocessor(BaseEstimator, TransformerMixin):
    """Deterministic sklearn-compatible text normalizer.

    URL and email presence are preserved as explicit tokens, with domain components retained as
    ordinary lexical tokens. Numbers become ``numtoken`` so numeric presence remains learnable.
    Porter stemming is used after stop-word removal because it is deterministic and requires no
    external corpus download; see the Day 3 decision record for the stemming/lemmatization trade-off.
    """

    def __init__(
        self,
        *,
        remove_html: bool = True,
        preserve_urls: bool = True,
        preserve_emails: bool = True,
        replace_numbers: bool = True,
        remove_stopwords: bool = True,
        stem_tokens: bool = True,
    ) -> None:
        self.remove_html = remove_html
        self.preserve_urls = preserve_urls
        self.preserve_emails = preserve_emails
        self.replace_numbers = replace_numbers
        self.remove_stopwords = remove_stopwords
        self.stem_tokens = stem_tokens
        self._stemmer = PorterStemmer()
        self._stopwords = set(ENGLISH_STOP_WORDS)
        self._stopwords.difference_update({"not", "no", "never"})

    def fit(self, X: Iterable[object], y: object = None) -> "TextPreprocessor":
        return self

    def preprocess_text(self, value: object) -> str:
        if _is_missing(value):
            return ""
        text = html.unescape(str(value)).casefold()
        if self.preserve_emails:
            text = EMAIL_PATTERN.sub(_replace_email, text)
        if self.preserve_urls:
            text = URL_PATTERN.sub(_replace_url, text)
        if self.remove_html:
            text = strip_html(text)
        if self.replace_numbers:
            text = NUMBER_PATTERN.sub(" numtoken ", text)
        text = remove_punctuation(text)
        tokens = text.split()
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self._stopwords]
        if self.stem_tokens:
            tokens = [self._stemmer.stem(token) for token in tokens]
        return " ".join(tokens)

    def transform(self, X: Sequence[object]) -> list[str]:
        return [self.preprocess_text(value) for value in X]
