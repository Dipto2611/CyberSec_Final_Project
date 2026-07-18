# Dataset Notes — Enterprise AI-Powered Phishing & Spam Detection System

> This document tracks dataset sources, label-mapping decisions, class balance, and any
> data-quality issues discovered during exploration. It is the authoritative reference for
> "why does our data look the way it does?"

---

## Dataset Sources

The project uses the single, locked dataset specified in the roadmap. It was downloaded in
its original standardized two-column form as two Parquet shards; no records were cleaned,
removed, or transformed during Day 2.

| Source | URL | Original Labels | Mapped Labels | Rows | Notes |
|--------|-----|-----------------|---------------|------|-------|
| The Biggest Spam Ham Phish Email Dataset (250000+) | https://www.kaggle.com/datasets/akshatsharma2/the-biggest-spam-ham-phish-email-dataset-300000 | `0` = Ham, `1` = Phish, `2` = Spam | `0` -> Safe, `1` -> Phishing, `2` -> Spam | 365,448 | MIT-licensed source dataset. Downloaded via its Hugging Face mirror because it provides direct Parquet access: https://huggingface.co/datasets/locuoco/the-biggest-spam-ham-phish-email-dataset-300000 |

## Label-Reconciliation Logic

The source is already natively three-class, so no datasets are merged and no label values are
changed in the raw data. For all future user-facing reporting:

| Raw label | Semantic meaning | Application label |
|-----------|------------------|-------------------|
| `0` | Ham / legitimate message | Safe |
| `1` | Phishing message | Phishing |
| `2` | Unsolicited spam | Spam |

## Class Balance

Class balance is calculated over all 365,448 raw records using the `label` column.

| Application class | Raw label | Records | Share of dataset |
|-------------------|-----------|--------:|-----------------:|
| Safe | `0` | 168,455 | 46.095477% |
| Phishing | `1` | 42,845 | 11.723966% |
| Spam | `2` | 154,148 | 42.180556% |

**Risk flagged:** Phishing is the minority class (11.724%). Later train/test splits and
iteration samples must be stratified, and evaluation must report phishing precision, recall,
and F1 separately rather than relying on aggregate accuracy.

## Text Length Distribution

Lengths are raw character counts. The two missing text values are excluded from length
calculations; they are intentionally retained for Day 3 missing-value handling.

| Class | Non-missing texts | Min | 25th percentile | Median | 75th percentile | 95th percentile | 99th percentile | Mean | Max |
|-------|------------------:|----:|----------------:|-------:|----------------:|----------------:|----------------:|-----:|----:|
| Safe | 168,454 | 1 | 454 | 986 | 1,992.75 | 6,226.00 | 18,447.10 | 2,183.19 | 11,510,306 |
| Phishing | 42,845 | 1 | 241 | 391 | 1,058.00 | 2,795.00 | 5,958.56 | 1,060.69 | 4,279,526 |
| Spam | 154,147 | 1 | 323 | 679 | 1,531.00 | 4,720.70 | 9,421.00 | 1,358.44 | 144,087 |

The distribution is strongly right-skewed, particularly for Safe and Phishing. This is
consistent with a corpus containing both short messages and full email threads or bodies;
the median is more representative than the mean for a typical message length.

## Day-to-Day Stratified Subsampling Strategy

Use a deterministic **60,000-record proportional stratified sample** for development and
model comparison after Day 3 cleaning. Create it with `random_state=42` and stratify on the
standardized label column. A 60,000-row sample is large enough to retain 7,035 phishing
examples while making repeated vectorization and model experiments practical on a student
development machine.

| Class | Records in 60,000-row iteration sample |
|-------|----------------------------------------:|
| Safe | 27,657 |
| Phishing | 7,035 |
| Spam | 25,308 |

The full 365,448-row dataset remains reserved for the final training/evaluation workflow.
The sample must preserve the original distribution; it must not be randomly downsampled per
class, because that would make reported production performance less representative.

## Known Data Quality Issues

- Two records have missing `text` values; labels are complete. They are not removed in Day 2.
- Text length has extreme outliers (up to 11,510,306 characters), likely full threads or
  unusually large message bodies. Day 3 will inspect and handle these deliberately rather
  than silently truncating them.
- The raw schema is exactly two columns: `label` (`int64`) and `text` (string).
- There are 84,490 duplicate full rows (approximately 23.12% of the corpus), and 84,498
  duplicate text values. No duplicates are removed in Day 2.
- Eight unique text values occur with conflicting labels, involving 20 rows. This label
  consistency risk must be investigated before training rather than resolved implicitly.
- There are no exact empty strings; one non-missing message contains whitespace only. This
  whitespace-only record was identified during the Day 3 pre-cleaning verification and was not
  modified in the raw source.

## Memory, Storage, and Provenance Verification

- Loading the combined dataset into pandas used 635,170,939 bytes (approximately 605.75 MiB).
- The two raw Parquet shards occupy 310,282,893 bytes (approximately 295.91 MiB) on disk.
- `0000.parquet` contains 300,000 rows and `0001.parquet` contains 65,448 rows. Both were
  written with `parquet-cpp-arrow version 21.0.0` and contain Hugging Face schema metadata.
- The local CSV at `D:\smsdataset.csv` was compared read-only with the combined Parquet
  shards. Both have shape `(365448, 2)`, columns `label` and `text`, matching dtypes,
  identical class counts, missing-value counts, duplicate count, row order, and row hashes.
  Therefore the Parquet shards contain exactly the same data as the CSV.
- The Parquet files are documented as downloaded from the Hugging Face mirror of the locked
  dataset, not generated from the CSV by this project. The CSV/Parquet equivalence is a
  verification result; neither source was modified.

## Engineering Review

The dataset is usable for the project, but it is not training-ready without an explicit Day 3
policy for missing text, duplicates, conflicting labels, and extreme length outliers. The
phishing class is a meaningful minority, so stratified sampling/splitting and per-class
metrics are required. Full-corpus pandas memory use is roughly 606 MiB before vectorization;
TF-IDF and model experiments may require substantially more memory, which supports using the
documented proportional development subset for iteration while retaining the full corpus for
the final workflow. Email bodies may also contain HTML, headers, forwarded threads, URLs, and
escape artifacts that will affect later preprocessing.

The 60,000-row proportional subset is a recommendation only. It has not been created or used,
and implementation requires approval after Day 3 cleaning decisions.

## Day 2 Engineering Decision Addendum

### Decision: Protect raw Parquet shards from accidental Git tracking
- Date: 2026-07-17
- Decision: Add `data/raw/*.parquet` to `.gitignore`.
- Reason: The verified raw shards are approximately 296 MiB on disk and belong to the immutable
  raw-data layer; tracking them in ordinary Git would create oversized repository history.
- Alternatives considered: Track the files directly; use Git LFS; leave the existing rule unchanged.
- Trade-offs: A fresh clone must obtain the locked raw data through the documented source process;
  Git LFS would add setup and hosting requirements outside today's scope.
- Impact on future development: Local profiling/training can continue from the raw directory,
  while source/provenance documentation remains version-controlled.

### Decision: Treat the CSV and Parquet shards as equivalent verified source copies
- Date: 2026-07-17
- Decision: Use the Parquet shards as the project's local profiling representation while retaining
  the CSV as an independently verified equivalent copy.
- Reason: Read-only comparison found identical schema, values, row order, hashes, counts, and
  missingness; Parquet also provides shard-level metadata and efficient columnar access.
- Alternatives considered: Re-profile only the CSV; re-export or rewrite either source; merge a
  different dataset.
- Trade-offs: Two copies require provenance documentation and storage, but the independent check
  reduces the risk of profiling an altered or partial file.
- Impact on future development: Day 3 must preserve the raw Parquet files and document any
  cleaned derivative separately; no source conversion is needed.

## Decisions Made

### Decision: Preserve native three-class labels and map them only for display
- Date: 2026-07-17
- Decision: Retain raw labels `0`, `1`, and `2` for data and modeling; use Safe, Phishing,
  and Spam only as human-readable application labels.
- Reason: The locked dataset is already standardized and natively three-class. Preserving
  source values prevents accidental label corruption while keeping the dashboard clear.
- Alternatives considered: Re-encode labels immediately; merge external datasets to change
  class counts.
- Trade-offs: Developers must remember the mapping when reading raw outputs, but the raw
  dataset remains traceable and no unnecessary transformation is introduced.
- Impact on future development: Day 3 validates the mapping; Days 4-6 use the numeric labels
  for training and translate predictions in the UI.

### Decision: Use a 60,000-row proportional stratified iteration sample
- Date: 2026-07-17
- Decision: Use a fixed-seed, 60,000-row stratified sample for iterative development, while
  reserving all raw records for the final training/evaluation workflow.
- Reason: The full corpus has 365,448 records and very long message outliers. Repeated model
  experiments are faster and more reproducible on a representative subset that still contains
  7,035 phishing records.
- Alternatives considered: Always train on all rows; use an unstratified random sample; use a
  class-balanced sample.
- Trade-offs: Iteration metrics are estimates rather than full-corpus metrics, but preserving
  the real class prevalence avoids misleading development results.
- Impact on future development: Days 4 and 5 use this sample with stratified splits; Day 6
  validates the chosen final artifact against the complete cleaned dataset.
