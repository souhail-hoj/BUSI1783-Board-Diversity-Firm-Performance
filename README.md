# BUSI1783 – Board Diversity and Firm Performance

## Project overview

This project examines the relationship between board diversity and firm performance among UK listed non-financial firms.

The final study uses a cross-sectional research design. The dataset contains 872 firms, with one observation for each firm at its most recent available fiscal year end (FY0).

The analysis considers several dimensions of board composition and examines their association with three measures of firm performance:

- Return on Assets (ROA)
- Return on Equity (ROE)
- Tobin's Q

## Research design

The project was initially planned as a panel study using firm-year observations. During data collection, access to LSEG Workspace expired approximately 48 hours after extraction began, before a multi-year panel could be constructed.

The research design was therefore revised to a cross-sectional study. Each firm contributes one observation at FY0.

The results should therefore be interpreted as cross-sectional associations rather than causal effects or within-firm changes over time.

## Variables

### Board diversity variables

- **Board Gender Diversity** – percentage of directors who are female.
- **Board Specific Skills** – percentage of directors identified as having sector-specific skills.

### Exploratory board variable

- **Policy Board Experience** – indicator for whether the board includes relevant policy or regulatory experience. This variable is treated as an exploratory proxy rather than as a direct measure of professional or experience diversity.

### Board characteristic

- **Board Size** – total number of directors.

### Firm-level controls

- **Firm Size** – firm-size measure provided in the source dataset and used as a control variable.
- **Leverage** – total debt as a percentage of total equity.
- **GICS Sector** – industry classification used to account for differences between sectors.

### Performance measures

- **ROA** – Return on Assets.
- **ROE** – Return on Equity.
- **Tobin's Q** – a market-based proxy for firm valuation, calculated from market capitalisation relative to total assets.

## Data sources

The project uses secondary company and financial data collected during the available extraction period.

LSEG Workspace was used for relevant board, diversity and company information before access expired. ORBIS was used for available firm-level financial and ownership information.

Kaggle was not used as a data source.

The original licensed source data are not redistributed through this public repository where their licensing conditions do not permit public redistribution.

## Data cleaning

The data preparation process included:

- checking company identifiers and duplicate observations;
- confirming the cross-sectional structure;
- checking missing observations;
- retaining the variables required for the research models;
- treating unavailable observations as missing rather than inventing or imputing unsupported values;
- excluding observations where required variables were unavailable for a particular regression;
- checking extreme observations and influential observations as part of the diagnostic analysis.

Ethnicity was considered as a possible diversity dimension, but sufficiently complete and defensible ethnicity data were not available within the accessible sources. No proxy variable was substituted.

## Statistical analysis

The analysis uses ordinary least squares (OLS) regression models to examine the association between board diversity and firm performance.

The models consider:

- board diversity variables;
- board size;
- firm size;
- leverage; and
- GICS sector fixed effects.

Heteroskedasticity-robust HC3 standard errors are used.

Additional statistical checks include:

- descriptive statistics;
- correlation analysis;
- variance inflation factor (VIF);
- Breusch–Pagan test;
- Cook's distance;
- outlier and influence checks; and
- sensitivity analysis.

The analysis is conducted separately for the three performance measures: ROA, ROE and Tobin's Q.

## Reproducibility

The repository documents the data preparation and statistical analysis procedures used for the BUSI1783 Business Analytics Project.

The analysis code is provided in the `analysis` folder.

The original licensed dataset is not included in the public repository. Researchers wishing to reproduce the analysis should obtain the relevant source data through the appropriate licensed data providers and prepare the dataset according to the procedures documented in this repository.

The results reported in the dissertation are based on the final cross-sectional dataset and the analysis procedures documented in this repository.

## Repository structure

```text
BUSI1783-Board-Diversity-Firm-Performance/
│
├── analysis/
│   ├── board_diversity_regression_analysis.py
│   └── board_diversity_regression_analysis.ipynb
│
├── data/
│   ├── BUSI1783_Cross_Sectional_Dataset.xlsx
│   └── README.md
│
├── README.md
│
└── requirements.txt
