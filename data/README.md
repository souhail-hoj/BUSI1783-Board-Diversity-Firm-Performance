# Data

The project dataset contains 872 UK non-financial listed firms observed cross-sectionally at FY0.

The data were collected from licensed secondary sources available during the project data-extraction period, including LSEG Workspace and ORBIS.

The cleaned dataset used for the analysis is included in this repository as BUSI1783_Cross_Sectional_Dataset.xlsx.

The dataset used for the analysis was cleaned before the statistical analysis. The cleaning process included checking firm identifiers and duplicate observations, confirming the cross-sectional structure, checking missing values, and retaining missing observations as missing rather than replacing them with unsupported values.

The final analysis uses complete cases separately for each regression model because the availability of variables differs across observations.

The analysis script is located in:

`analysis/board_diversity_regression_analysis.py`

Kaggle was not used as a data source.
