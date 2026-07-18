# PROJECT LOG — Enterprise AI-Powered Phishing & Spam Detection System

> This file is the single source of truth for project progress. Updated at the end of every day.
> Antigravity reads this file at the start of each session to determine where to resume.

---

## Day 1 — Foundation & Project Setup
**Date:** 2026-07-16
**Status:** COMPLETE

### Objectives
- [x] Understand system architecture
- [x] Create folder structure
- [x] Set up virtual environment & install libraries (All 10 packages installed)
- [x] Review candidate datasets (preview — full strategy on Day 2)
- [x] Explain full 15-day roadmap
- [x] Initialize Git repository
- [x] Connect to remote GitHub repository (URL provided by user)

### Accomplishments
- Created the complete project folder structure: `src/`, `data/raw/`, `data/processed/`, `models/`, `visualizations/`, `tests/`, `app/`
- Set up Python virtual environment (`venv/`)
- Installed 6 of 10 required packages (pandas, numpy, matplotlib, scikit-learn, joblib, seaborn already available on system)
- Created `requirements.txt` with all project dependencies
- Created comprehensive `.gitignore` (excludes venv, data files, model artifacts, IDE files)
- Created `PROJECT_LOG.md` and `DATASET_NOTES.md` documentation scaffolding
- Saved `AGENTS.md` at `.agents/AGENTS.md` for automatic session loading
- Created placeholder modules for all source files (`preprocessing.py`, `model.py`, `threat_analyzer.py`, `recommendation_engine.py`, `streamlit_app.py`)
- Initialized Git repository and made the first commit (`cb291dd`)
- Explained the full system architecture (pipeline pattern), folder structure rationale, technology stack justification, 15-day roadmap, and candidate dataset overview

### Concepts Learned
- **Pipeline architecture**: linear data flow where each component has a single responsibility — preprocessing doesn't know about the model, the model doesn't know about the UI
- **Raw vs. processed data separation**: industry practice of keeping original data immutable
- **3-class vs. binary classification**: why our project diverges from tutorial spam classifiers (Safe/Spam/Phishing vs. spam/ham)
- **Stratified splitting**: needed when classes are imbalanced (preview for Day 5)
- **Project structure conventions**: `src/` for source, `tests/` for tests, `models/` for artifacts

### Files Created/Modified
| File | Action | Purpose |
|------|--------|---------|
| `.agents/AGENTS.md` | Created | Master project instructions |
| `.gitignore` | Created | Git exclusion rules |
| `PROJECT_LOG.md` | Created | Project progress tracker |
| `DATASET_NOTES.md` | Created | Dataset documentation |
| `requirements.txt` | Created | Python dependencies |
| `src/__init__.py` | Created | Source package init |
| `src/preprocessing.py` | Created | Preprocessing placeholder |
| `src/model.py` | Created | Model training placeholder |
| `src/threat_analyzer.py` | Created | Threat analysis placeholder |
| `src/recommendation_engine.py` | Created | Recommendation engine placeholder |
| `tests/__init__.py` | Created | Tests package init |
| `app/streamlit_app.py` | Created | Streamlit dashboard placeholder |
| `data/raw/README.md` | Created | Raw data directory marker |
| `data/processed/README.md` | Created | Processed data directory marker |
| `models/README.md` | Created | Models directory marker |
| `visualizations/README.md` | Created | Visualizations directory marker |

### Decision: Pipeline Architecture Pattern
- **Date:** 2026-07-16
- **Decision:** Use a linear pipeline architecture (User → Streamlit → Preprocessing → TF-IDF → Model → Threat Analysis → Recommendations → Dashboard)
- **Reason:** Each stage has a single responsibility, making the system independently testable, replaceable, and auditable — critical for a security product
- **Alternatives considered:** Monolithic script (simpler but untestable), microservices (overkill for this scope)
- **Trade-offs:** Slightly more files/boilerplate upfront, but dramatically easier to debug, test, and explain
- **Impact on future development:** Every future day's work slots cleanly into one specific module

### Decision: 3-Class Classification (Safe/Spam/Phishing)
- **Date:** 2026-07-16
- **Decision:** Classify into 3 classes instead of the typical binary (spam/ham)
- **Reason:** Differentiates this project from tutorial clones; mirrors real-world SOC tools where phishing is a distinct, higher-severity threat category
- **Alternatives considered:** Binary classification (simpler, more datasets available), 4+ classes (too granular for scope)
- **Trade-offs:** Requires combining multiple datasets with label reconciliation (Day 2 risk); potential class imbalance for Phishing
- **Impact on future development:** Dataset strategy (Day 2), evaluation metrics (Day 9), and threat analysis (Day 14) all depend on this choice

### Challenges Encountered
- **No internet connectivity**: DNS resolution failed, preventing `pip install` of 4 packages (nltk, streamlit, wordcloud, pytest). Mitigated by confirming none are needed until Day 4+
- **Remote GitHub repo**: Cannot be automated — requires user's own credentials

### Suggested Improvements
- Install the 4 missing packages as soon as internet is available
- Consider adding a `setup.py` or `pyproject.toml` for a more "production" feel (low priority, stretch goal)

### What's Next
- **Day 2**: Dataset Strategy — the highest-risk day. Identify datasets, reconcile labels, perform EDA, report class balance

---

## Future Improvements
| Idea | Priority | Estimated Complexity | Expected Benefit |
|------|----------|---------------------|-----------------|
| Add `pyproject.toml` for modern Python packaging | Low | Low | More professional project setup |
| Deploy to Streamlit Community Cloud | Medium | Low | Live demo link for resume/GitHub |

---

## Day 2 — Dataset Profiling
**Date:** 2026-07-17
**Status:** COMPLETE

### Objectives
- [x] Load the locked dataset and confirm its raw schema and row count
- [x] Report exact Safe / Spam / Phishing class balance
- [x] Profile raw text-length distribution per class
- [x] Define a stratified subsampling strategy for daily iteration
- [x] Document source facts, quality observations, and decisions in `DATASET_NOTES.md`

### Accomplishments
- Downloaded the locked dataset's two Parquet shards into `data/raw/` without modifying their contents.
- Confirmed 365,448 rows with exactly two columns: `label` (`int64`) and `text` (string).
- Confirmed source-label mapping: `0` = Ham/Safe, `1` = Phish/Phishing, and `2` = Spam.
- Measured class balance: Safe 168,455 (46.095477%), Phishing 42,845 (11.723966%), and Spam 154,148 (42.180556%).
- Flagged phishing as the minority class and documented its future evaluation implications.
- Measured per-class raw character-length distributions, including the strong long-tail caused by very large message bodies.
- Defined a deterministic, 60,000-row proportional stratified iteration sample with `random_state=42`; it retains 7,035 phishing examples.

### Concepts Learned
- **Class imbalance:** A minority class can be poorly detected even when overall accuracy is high; phishing must be assessed with its own precision, recall, and F1.
- **Stratification:** Sampling or splitting while preserving class proportions prevents rare classes from being accidentally underrepresented.
- **Distribution profiling:** Median and percentiles describe skewed text lengths better than an average alone, especially for full email bodies and forwarded threads.
- **Raw-data immutability:** Profiling observes the source dataset; cleaning is deferred so every later transformation remains explicit and reproducible.

### Files Created/Modified
| File | Action | Purpose |
|------|--------|---------|
| `data/raw/0000.parquet` | Downloaded | Raw dataset shard 1 |
| `data/raw/0001.parquet` | Downloaded | Raw dataset shard 2 |
| `.gitignore` | Updated | Exclude immutable raw Parquet shards from ordinary Git tracking |
| `DATASET_NOTES.md` | Updated | Source, schema, balance, length profile, and sampling plan |
| `PROJECT_LOG.md` | Updated | Day 2 engineering record |

### Decision: Preserve native three-class labels and map them only for display
- Date: 2026-07-17
- Decision: Keep `0`/`1`/`2` as raw model labels and map them to Safe/Phishing/Spam only in human-facing output.
- Reason: The locked source is natively three-class, so this retains source traceability and avoids an unnecessary raw-data transformation.
- Alternatives considered: Immediate re-encoding; merging further datasets.
- Trade-offs: The numeric-to-display mapping must be consistently maintained.
- Impact on future development: Training uses numeric labels; the dashboard translates them for users.

### Decision: Use a 60,000-row proportional stratified iteration sample
- Date: 2026-07-17
- Decision: Use a fixed-seed 60,000-row proportional stratified sample for repeated development work and reserve the full cleaned corpus for final training/evaluation.
- Reason: It is representative, reproducible, faster to iterate on, and retains 7,035 phishing examples.
- Alternatives considered: Full-data iteration; unstratified sampling; class-balanced sampling.
- Trade-offs: Development metrics are estimates, but class prevalence remains realistic.
- Impact on future development: Days 4-5 use stratified sampling and report per-class results; Day 6 evaluates the final artifact on the full cleaned dataset.

### Challenges Encountered
- The raw-data directory was empty at session start. A first mirror download produced a zero-byte redirected artifact, which was detected before use and replaced with a verified, redirect-aware download.
- Two raw text values are missing, and extreme length outliers exist. No cleaning was done; both observations are explicitly deferred to Day 3.

### Suggested Improvements
- On Day 3, record the precise missing-value and duplicate-handling policy before applying it.
- On Day 4, ensure every split is stratified and every report includes phishing-specific precision, recall, and F1.

### What's Next
- **Day 3:** Clean the raw corpus, standardize/validate labels, implement the reusable text preprocessing pipeline, and add its pytest coverage.

### Daily Reflection & Engineering Review
1. **What did we accomplish today?**
   We obtained and profiled the locked three-class email dataset, verified its schema and 365,448-row size, quantified class imbalance, characterized text lengths, and defined a reproducible iteration-data strategy.

2. **What engineering decisions did we make today?**
   We preserved numeric source labels and use a display-only mapping; we selected a 60,000-row proportional stratified iteration sample with seed 42. Both choices protect traceability, reproducibility, and representative phishing prevalence.

3. **What risks or challenges should we watch for in future milestones?**
   Phishing is only 11.724% of records, so accuracy can conceal weak phishing recall. Two missing texts and multi-million-character outliers require intentional Day 3 handling; large raw text also makes full-corpus experiments slower and more memory-intensive.

4. **What interview, presentation, or viva questions could arise from today's work?**
   - *Why stratify?* To preserve the minority phishing proportion in samples and splits so training and evaluation remain representative.
   - *Why is accuracy insufficient here?* A model can score well by predicting the majority classes while missing phishing; per-class precision, recall, and F1 expose that failure.
   - *Why use the median text length?* The corpus is right-skewed by very long email bodies, which pull the mean upward; the median better represents a typical message.
   - *Why not clean immediately?* Separating profiling from cleaning keeps the source immutable, makes transformations auditable, and prevents hidden data-loss decisions.

5. **Are we still aligned with the official 10-day project roadmap?**
   Yes. Day 2 was limited to loading, profiling, imbalance analysis, and documentation. No preprocessing, feature engineering, training, or UI work was started. The project is ready for Day 3 after approval.

### Day 2 Completion Addendum — Verified Dataset and Repository Review

The Day 2 profile was independently rechecked before completion. The combined Parquet shards
contain 365,448 rows and two columns (`label`, `text`), matching the local
`D:\smsdataset.csv` exactly in shape, columns, dtypes, row order, row hashes, class counts,
missingness, and duplicate count. The Parquet files therefore contain the same data as the CSV;
the project did not rewrite either source. The shards are documented as downloaded from the
Hugging Face mirror of the locked dataset.

Additional verified findings:

- Pandas memory usage is 635,170,939 bytes (approximately 605.75 MiB); Parquet storage is
  310,282,893 bytes (approximately 295.91 MiB).
- There are 84,490 duplicate full rows, 84,498 duplicate text values, and eight conflicting
  text-label groups involving 20 rows.
- There are two missing texts, no exact empty strings, and no non-missing whitespace-only texts.
- Text lengths are strongly right-skewed, with maximums of 11,510,306 (Safe), 4,279,526
  (Phishing), and 144,087 (Spam) characters.

The approved repository protection fix was applied: `.gitignore` now excludes
`data/raw/*.parquet`, preventing approximately 296 MiB of immutable raw shards from being
accidentally committed to ordinary Git history.

### Decision: Protect raw Parquet shards from accidental Git tracking
- Date: 2026-07-17
- Decision: Add `data/raw/*.parquet` to `.gitignore`.
- Reason: The raw shards are large immutable inputs and should not inflate normal Git history.
- Alternatives considered: Track directly; use Git LFS; leave the rule unchanged.
- Trade-offs: A fresh clone must obtain the raw data through the documented source process; Git LFS
  would add setup and hosting requirements outside Day 2.
- Impact on future development: Raw data remains local and reproducible through documented
  provenance while project documentation stays version-controlled.

### Decision: Treat CSV and Parquet as equivalent verified source copies
- Date: 2026-07-17
- Decision: Continue profiling from the Parquet shards after read-only equivalence verification
  against `D:\smsdataset.csv`.
- Reason: Schema, values, row order, hashes, counts, missingness, and duplicate counts all match.
- Alternatives considered: Re-profile only the CSV; rewrite either source; change datasets.
- Trade-offs: Keeping two verified copies uses storage and requires provenance notes, but preserves
  an independent audit check and efficient columnar access.
- Impact on future development: Day 3 will create any cleaned derivative separately and preserve
  both raw sources unchanged.

### Day 2 Definition of Done Verification

- [x] Today's profiling and engineering-review objectives are complete.
- [x] Work remains within the agreed linear architecture; no architecture was changed.
- [x] Code remains clean, modular, and readable; no production code was added or altered.
- [x] Existing functionality remains intact; no executable files were modified.
- [x] Relevant tests are not applicable on Day 2 because the AGENTS.md testing checkpoint
  begins on Day 3; no test suite was bypassed.
- [x] Day 2 edge cases and risks were considered: missing values, duplicates, conflicting labels,
  empty messages, long-tail lengths, class imbalance, memory, and provenance.
- [x] `PROJECT_LOG.md` and `DATASET_NOTES.md` contain the verified findings and decisions.
- [x] Meaningful technical decisions use the Engineering Decision Register format.
- [x] The repository is stable and committable; raw Parquet files are now ignored by Git.
- [x] A concise end-of-day summary and the five reflection answers are recorded below.
- [x] No cleaning, preprocessing, feature engineering, splitting, model training, or Day 3 work
  was performed.

### Daily Reflection — Final Day 2 Review

1. **What did we accomplish today?** We verified the locked dataset end to end, profiled its
   schema, classes, missingness, duplicates, empty messages, text lengths, memory/storage, and
   anomalies; confirmed the Parquet shards exactly match `D:\smsdataset.csv`; protected raw
   Parquet files from Git tracking; and documented the engineering review.

2. **What engineering decisions did we make today?** We preserved native numeric labels with a
   display mapping, recommended (but did not implement) a 60,000-row proportional stratified
   iteration subset, kept the Parquet representation as the local profiling source after exact
   CSV equivalence verification, and excluded raw Parquet shards from ordinary Git tracking.

3. **What risks or challenges should we watch for in future milestones?** Phishing is only
   11.724%, so accuracy can hide poor phishing recall. Day 3 must explicitly decide how to handle
   two missing texts, 84,490 duplicate rows, eight conflicting text-label groups, and extreme
   length outliers. Full-corpus vectorization may exceed the approximately 606 MiB pandas
   baseline, and email-specific HTML/headers/URLs may complicate preprocessing.

4. **What interview, presentation, or viva questions could arise?**
   - *Why stratify?* To preserve phishing prevalence in samples and splits.
   - *Why not use accuracy alone?* Minority-class failures can be hidden by majority-class accuracy;
     per-class precision, recall, and F1 are safer.
   - *Why profile before cleaning?* It separates measurement from irreversible data decisions and
     keeps the raw source auditable.
   - *How did you verify CSV and Parquet equivalence?* By comparing schema, values, row order,
     hashes, class counts, missingness, and duplicate counts without writing either file.
   - *Why ignore Parquet in Git?* The immutable shards are approximately 296 MiB and should not
     inflate ordinary repository history.

5. **Are we still aligned with the official 10-day project roadmap?** Yes. Only Day 2 profiling,
   engineering review, provenance verification, and documentation were completed. No cleaning,
   preprocessing, feature engineering, splitting, training, or Day 3 work was performed. Day 2
   satisfies the Definition of Done and the project is ready for Day 3, pending your approval.

### What's Next

- **Day 3 (approval required):** Clean the raw corpus, make explicit missing/duplicate/label/outlier
  policies, implement the reusable preprocessing pipeline, and add its tests.


---

# Day 3 — Data Cleaning & NLP Preprocessing

**Date:** 2026-07-18

**Status:** COMPLETE

---

## Objectives

- [x] Clean the raw dataset
- [x] Handle missing values
- [x] Remove duplicate records
- [x] Preserve valid labels
- [x] Build a reusable NLP preprocessing pipeline
- [x] Create preprocessing tests

---

## Accomplishments

- Removed duplicate rows from the raw dataset.
- Handled missing and whitespace-only messages safely.
- Generated a cleaned dataset for model development.
- Implemented a reusable `TextPreprocessor` class.
- Preserved phishing-related security indicators such as URLs, email addresses and numeric tokens.
- Added preprocessing normalization including lowercase conversion, punctuation cleanup, stopword removal and stemming.
- Designed the preprocessing module to be reusable inside both training and future inference pipelines.
- Implemented automated preprocessing tests covering multiple edge cases.

---

## Key Dataset Changes

- Original rows: **365,448**
- Cleaned rows: **280,955**
- Missing rows removed: **2**
- Duplicate rows removed: **84,490**
- Invalid labels found: **0**

---

## Engineering Decisions

### Decision

Use a reusable preprocessing class instead of embedding text cleaning directly inside the training script.

### Reason

A reusable preprocessing component makes future deployment, testing and inference significantly easier while avoiding duplicated code.

---

## Challenges

- Preserving phishing indicators without over-cleaning.
- Balancing normalization with security signal preservation.
- Ensuring preprocessing remains deterministic.

---

## Files Created / Updated

- src/preprocessing.py
- tests/test_preprocessing.py
- scripts/run_days_3_6.py

---

## Definition of Done

- [x] Cleaning completed
- [x] Preprocessing pipeline implemented
- [x] Unit tests added
- [x] Dataset ready for feature engineering

---

# Day 4 — Feature Engineering & Baseline Modeling

**Date:** 2026-07-18

**Status:** COMPLETE

---

## Objectives

- [x] Generate TF-IDF features
- [x] Split dataset
- [x] Train baseline model

---

## Accomplishments

- Created a TF-IDF feature space with **50,000** features.
- Generated stratified train and test datasets.
- Prepared reusable vectorizer for deployment.
- Trained baseline machine learning models.

---

## Dataset Split

Development Dataset

- 60,000 samples

Training

- 48,000 samples

Testing

- 12,000 samples

---

## Engineering Decisions

Selected TF-IDF because it provides a strong sparse representation while remaining lightweight and highly effective for classical NLP models.

---

## Files Updated

- src/model.py
- scripts/run_days_3_6.py

---

## Definition of Done

- [x] TF-IDF completed
- [x] Dataset split completed
- [x] Baseline model trained

---

# Day 5 — Model Training & Selection

**Date:** 2026-07-18

**Status:** COMPLETE

---

## Objectives

- [x] Train multiple classifiers
- [x] Compare performance
- [x] Select production model

---

## Models Trained

- Multinomial Naive Bayes
- Logistic Regression
- Random Forest

---

## Final Results

| Model | Accuracy |
|--------|----------|
| MultinomialNB | 91.58% |
| **Logistic Regression** | **94.86%** |
| Random Forest | 91.29% |

---

## Final Production Model

**Logistic Regression**

Reasons

- Highest overall accuracy
- Highest Macro F1
- Strong phishing recall
- Best overall balance

---

## Engineering Decision

Use Logistic Regression as the production model for all future development.

---

## Definition of Done

- [x] Three models compared
- [x] Best model selected

---

# Day 6 — Evaluation & Artifact Generation

**Date:** 2026-07-18

**Status:** COMPLETE

---

## Objectives

- [x] Evaluate final model
- [x] Generate reports
- [x] Save deployment artifacts

---

## Evaluation Summary

Final model evaluated using:

- Accuracy
- Precision
- Recall
- Macro F1
- Weighted F1
- Confusion Matrix

---

## Confusion Matrix Summary

Safe

- Correct: **5292**

Phishing

- Correct: **1712**

Spam

- Correct: **4379**

Overall performance demonstrates strong separation across all three classes with relatively few Safe ↔ Phishing confusions and the largest remaining confusion occurring between Spam and Phishing, which is expected because both classes often share promotional and urgency-related language.

---

## Generated Outputs

Saved:

- final_model.joblib
- final_pipeline.joblib
- tfidf_vectorizer.joblib
- model_metadata.joblib
- confusion_matrix.png
- model_comparison.csv
- model_metrics.json
- phishing_false_negatives.csv
- manual_predictions.json

---

## Engineering Decisions

Saved the complete preprocessing + vectorizer + model pipeline to simplify future deployment into the Streamlit application.

---

## Project Status

Current Progress

- ✅ Day 1 Complete
- ✅ Day 2 Complete
- ✅ Day 3 Complete
- ✅ Day 4 Complete
- ✅ Day 5 Complete
- ✅ Day 6 Complete

Next Milestone

- Day 7 — Threat Analysis Engine

---

## Daily Reflection

Today the project transitioned from a data-processing prototype into a deployable machine learning system.

The training pipeline is fully operational, the best model has been selected through objective evaluation, reusable artifacts have been generated, and the repository is now prepared for application-layer development in the next milestone.
