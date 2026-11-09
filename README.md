# Health Claim Cost Model

Models for annual health care spending, built on the MEPS (Medical Expenditure Panel Survey) public-use files. The main question: how well can demographics, coverage, and health status predict what a person spends in a year, and how much of that is captured by GLM versus gradient-boosting approaches?

**Status:** modeling and exploration are complete. Remaining work is listed under [Next steps](#next-steps).

## Results (2024 adults, trained on 2023)

| Model | Weighted MAE | Tweedie deviance | A/E | Top 5% capture |
|---|---|---|---|---|
| Baseline (mean for everyone) | $10,758 | 247.5 | 1.16 | 5.0% |
| Two-part GLM | $9,278 | 182.2 | 1.11 | 16.4% |
| Tweedie GLM | $9,253 | 182.6 | 1.12 | 16.1% |
| XGBoost (Tweedie) | $8,898 | 182.0 | 1.22 | 17.1% |
| LightGBM (Tweedie) | $8,857 | 181.0 | 1.23 | 17.7% |

- **MAE** is the average absolute miss per person. **Deviance** is the Tweedie loss the boosting models are fit on. **A/E** is actual total divided by predicted total (1.0 = calibrated). **Top 5% capture** is the share of spending from the 5% of people the model ranks highest; a perfect ranking would capture about 46%.
- Every model clearly beats the baseline. The boosting models are slightly ahead, but their bootstrap intervals overlap the GLMs'.
- **All models under-predict 2024 spending** (A/E above 1). Average adult spending rose about 14% from 2023 to 2024, and the models were fit to 2023 levels. This is a level shift, not a model error. Relative to each model's own overall level, the segments are within about 10%, except that the GLMs over-predict people 65 and older (about 0.87 to 0.88) and under-predict adults 18 to 49 (1.06 to 1.13).
- Results on people who weren't in the 2023 survey panel are nearly identical (see `data/processed/model_metrics.csv`).

## What drives spending

Age, self-rated health, arthritis, the poverty ratio, and insurance coverage are the top features in both boosting models. In the two-part GLM, controlling for other factors:
- **Uninsured:** odds of any spending about 0.24 times the privately insured; amount among spenders about 0.37 times.
- **Poor self-rated health:** odds of spending 1.77 times; amount 3.26 times.
- **Cancer:** odds of spending 2.88 times; amount 1.59 times.
- **Women:** odds of spending 1.54 times; amount 1.20 times.

These are associations. Health and diagnoses are measured in the same year as spending.

## Data

Raw data lives in `data/` and is **not** in git (the folder is gitignored). Download it again on a new machine:

| Dataset | Location | Source | Used for |
|---|---|---|---|
| MEPS Full Year Consolidated, 2020 to 2024 | `data/raw/meps/<year>/h<nnn>.dta` (plus codebook and documentation PDFs) | [AHRQ MEPS data files](https://meps.ahrq.gov/mepsweb/data_stats/download_data_files.jsp) | **Main analysis and models** |
| Kaggle "Medical Cost Personal Datasets" | `data/raw/kaggle/insurance.csv` | `kaggle datasets download -d mirichoi0218/insurance` | Early practice; loaded to `data/processed/insurance.db` but not used in the models |
| DE-SynPUF Sample 1 (CMS) | `data/raw/synpuf/` | [CMS SynPUF downloads](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/DESample01) | Downloaded; not analyzed yet |

MEPS files are the Stata (`.dta`) versions. Each year's `h<nnn>` code is 224 (2020), 233 (2021), 243 (2022), 251 (2023), and 256 (2024).

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                  # creates .venv and installs everything in uv.lock (including ipykernel)
# then open the notebooks in VS Code and select the .venv interpreter as the kernel
```

Notebooks read data with paths relative to `notebooks/`, so run them from inside `notebooks/` or from VS Code. `src/load_meps.py` builds paths from its own location.

**Known workaround:** scikit-learn and XGBoost gradient boosting hung on WSL2 with multiple threads. Each notebook that uses them sets `OMP_NUM_THREADS=1` before importing. Keep that line at the top.

## Notebooks

Run in this order:

1. **`01_meps_exploration.ipynb`**: the first look at MEPS 2023 spending variables, the payer reconciliation, and the spending distribution.
2. **`02_tot_figures.ipynb`**: the exploration itself, one section per variable group (payers, age, sex, region, education, income, marital status, diagnoses, smoking, insurance, health status, employment), cross-variable patterns, and a **Conclusions** section listing the target, candidate predictors, cleaning rules, and open decisions. Read this one first.
3. **`03_models.ipynb`**: the models. Settings, feature list, and every decision are at the top. Includes two-part GLM, Tweedie GLM, XGBoost, LightGBM, evaluation on 2024, calibration, gains curve, and findings.

## Key decisions

These are the defaults used in the models. The conclusions notebook lists which ones were still open.

- **Target:** total spending `TOTEXP`, all payers. The alternative, private-insurance payments (`TOTPRV`), was not modeled.
- **Population:** adults 18 and over. Diagnosis, lifestyle, and marital questions are adult-only.
- **Timing:** concurrent. Same-year features predict same-year spending. The model describes a relationship; it isn't a forecast.
- **Features:** age, sex, region, marital status, poverty ratio (`POVLEV`), coverage, highest degree (`HIDEG`), general and mental health (round 31), 10 diagnosis flags, smoking, employment (round 31, imputed version). `FAMINC` and `POVCAT` were dropped because `POVLEV` carries nearly the same information. `EDUCYR` and race were left out.
- **Excluded from features:** all payer and expenditure columns (they're parts of the outcome), survey design columns, and the person ID.
- **Weights:** `PERWT` in every fit and every average. GLM fits use weights scaled to average 1, which is needed for convergence and doesn't change estimates.
- **Splits:** train on 2023 adults (with 20% held out for early stopping), test on 2024 adults. A second test set uses only 2024 people who weren't in the 2023 survey panel. About 47% of 2023 people appear in 2024.
- **Cleaning:** special codes -7, -8, and -15 are treated as missing, and rows with invalid codes are dropped. -1 (inapplicable) is handled by the adult restriction.

## Known limitations

- **Level shift:** 2024 spending is about 14% higher than 2023. No trend adjustment is applied.
- **Standard errors are approximate.** The GLMs use cluster-robust errors, but statsmodels warns that clustering isn't fully supported with frequency weights. The bootstrap resamples people, not PSUs, so its intervals are probably too narrow.
- **Light tuning.** Boosting settings were chosen up front. There's no cross-validated search, and the final boosting models weren't refit on all of 2023.
- **One test year** (2024).
- **Adults only.** Children aren't modeled.
- **Race and ethnicity** aren't in the models and no fairness check has been run.
- **Ranking the top spenders is weak:** the best models capture about 18% of spending in their top 5% of predictions, against a ceiling of about 46%.

## Next steps

1. Add an explicit trend or level adjustment for 2024, and state the assumption.
2. Cross-validate the boosting models on 2023, grouped by PSU, to tune settings.
3. Refit the boosting models on all of 2023 at the chosen number of trees.
4. Build a separate model for children.
5. Check fairness across race and ethnicity.
6. Use the SynPUF data for a second project, or for claim-level modeling.
7. Write up the results for a resume or portfolio page.

## Repository layout

```
notebooks/          01 to 03 analysis and models (see above)
src/load_meps.py    loads one MEPS year from data/raw/meps
data/               raw and processed data (gitignored)
figures/            charts saved from the exploration (committed)
pyproject.toml      dependencies (uv)
uv.lock             exact resolved versions
```

## Working conventions

- Dependencies are managed with `uv add <package>` and `uv remove <package>`, so `pyproject.toml` and `uv.lock` stay in sync.
- Commit `pyproject.toml` and `uv.lock` together when dependencies change.
- Earlier lesson notebooks were removed from the working tree but remain in git history (commit `e2afe11` and earlier).
