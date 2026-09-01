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

- Board Gender Diversity – percentage of directors who are female.
- Board Specific Skills – percentage of directors identified as having sector-specific skills.
- Policy Board Experience – indicator for whether the board includes relevant policy or regulatory experience.
- Board Size – total number of directors.

### Firm-level controls

- Firm Size – log of total assets.
- Leverage – total debt as a percentage of total equity.
- GICS Sector – industry classification used to account for sector differences.

### Performance measures

- ROA – Return on Assets.
- ROE – Return on Equity.
- Tobin's Q – market-based measure of firm valuation.

## Data sources

The project uses secondary company and financial data collected during the available extraction period.

LSEG Workspace was used for relevant board and diversity information before access expired. ORBIS was used for available firm financial and ownership information, and company annual reports were consulted where individual disclosures required clarification.

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

The models include:

- board diversity variables;
- board size;
- firm size;
- leverage; and
- GICS sector fixed effects.

Heteroskedasticity-robust HC3 standard errors are used.

Additional diagnostic checks include:

- correlation analysis;
- variance inflation factor (VIF);
- Breusch–Pagan test;
- Cook's distance; and
- sensitivity analysis using trimmed dependent-variable samples.

## Reproducibility

The repository is intended to document the data preparation and statistical analysis process used for the BUSI1783 Business Analytics Project.

The analysis results reported in the dissertation are based on the final cross-sectional dataset and the analysis procedures documented in this repository.

## Limitations

The main methodological limitations are:

1. The cross-sectional design does not allow within-firm changes to be analysed.
2. The results should not be interpreted as evidence of causality.
3. Board-composition variables contain substantial missingness for some measures.
4. Ethnicity could not be incorporated because sufficiently complete data were unavailable.
5. The original planned panel design could not be completed because access to LSEG Workspace expired during data extraction.

## Academic project

Module: BUSI1783 – Business Analytics Project

Research topic: Board Diversity and Firm Performance

Study design: Cross-sectional statistical analysis of UK non-financial listed firms.
