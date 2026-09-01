from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import OLSInfluence, variance_inflation_factor


# ---------------------------------------------------------------------
# Project settings
# ---------------------------------------------------------------------

DATA_FILE = Path("BUSI1783_Cross_Sectional_Dataset.xlsx")
OUTPUT_DIR = Path("outputs")


# ---------------------------------------------------------------------
# Data loading and cleaning
# ---------------------------------------------------------------------

def normalise_name(value):
    """Standardise a column name for matching."""
    return " ".join(str(value).replace("\n", " ").split()).strip().lower()


def load_data(file_path):
    """Load the Dataset sheet and standardise the variable names."""
    df = pd.read_excel(file_path, sheet_name="Dataset")

    expected = {
        "identifier (ric)": "RIC",
        "company name": "Company_Name",
        "country of headquarters": "Country",
        "gics sector name": "GICS_Sector",
        "board gender diversity, percent (fy0)": "Gender_Diversity",
        "return on assets": "ROA",
        "roe": "ROE",
        "tobins_q": "Tobins_Q",
        "firm size": "Firm_Size",
        "board size (fy0)": "Board_Size",
        "board specific skills, percent (fy0)": "Specific_Skills",
        "policy board experience (fy0)": "Policy_Experience",
        "total debt percentage of total equity (fy0)": "Leverage",
        "fiscal year end date": "FY_End",
    }

    lookup = {normalise_name(c): c for c in df.columns}

    rename = {}

    for source_name, new_name in expected.items():
        if source_name in lookup:
            rename[lookup[source_name]] = new_name

    df = df.rename(columns=rename)

    numeric_columns = [
        "Gender_Diversity",
        "ROA",
        "ROE",
        "Tobins_Q",
        "Firm_Size",
        "Board_Size",
        "Specific_Skills",
        "Leverage",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Policy Board Experience is a binary 0/1 field.
    # Handle both numeric values and text representations.
    if "Policy_Experience" in df.columns:
        policy_numeric = pd.to_numeric(
            df["Policy_Experience"],
            errors="coerce"
        )

        policy_text = (
            df["Policy_Experience"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        text_mapping = {
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0,
            "1.0": 1,
            "0.0": 0,
        }

        policy_text = policy_text.map(text_mapping)

        df["Policy_Experience"] = policy_numeric.fillna(policy_text)

    return df


# ---------------------------------------------------------------------
# Model specification
# ---------------------------------------------------------------------

PREDICTORS = [
    "Gender_Diversity",
    "Specific_Skills",
    "Board_Size",
    "Policy_Experience",
    "Firm_Size",
    "Leverage",
]

OUTCOMES = [
    "ROA",
    "ROE",
    "Tobins_Q",
]


def make_design_matrix(data):
    """
    Create the regression design matrix.

    The model includes:
    - six board/firm predictors
    - GICS sector fixed effects
    - an intercept
    """
    x = data[PREDICTORS].astype(float).copy()

    sector_dummies = pd.get_dummies(
        data["GICS_Sector"].astype(str),
        prefix="Sector",
        drop_first=True,
        dtype=float,
    )

    x = pd.concat([x, sector_dummies], axis=1)

    x.insert(0, "Intercept", 1.0)

    return x


# ---------------------------------------------------------------------
# OLS with HC3 robust standard errors
# ---------------------------------------------------------------------

def run_ols(data, outcome):
    """Estimate the main OLS model using HC3 robust standard errors."""

    required = [outcome, "GICS_Sector"] + PREDICTORS

    sample = data.dropna(subset=required).copy()

    x = make_design_matrix(sample)
    y = sample[outcome].astype(float)

    model = sm.OLS(y, x).fit(cov_type="HC3")

    coefficients = pd.DataFrame({
        "Variable": x.columns,
        "Coefficient": model.params.values,
        "HC3_SE": model.bse.values,
        "t": model.tvalues.values,
        "p": model.pvalues.values,
    })

    return model, coefficients, sample, x


# ---------------------------------------------------------------------
# Correlations
# ---------------------------------------------------------------------

def correlation_analysis(data):
    """Calculate pairwise Pearson correlations."""

    correlation_columns = [
        "ROA",
        "ROE",
        "Tobins_Q",
        "Gender_Diversity",
        "Specific_Skills",
        "Board_Size",
        "Policy_Experience",
        "Firm_Size",
        "Leverage",
    ]

    available = [
        column for column in correlation_columns
        if column in data.columns
    ]

    return data[available].corr(method="pearson")


# ---------------------------------------------------------------------
# VIF
# ---------------------------------------------------------------------

def calculate_vif(sample):
    """
    Calculate VIF for the six substantive predictors.

    Sector dummy variables are excluded from the reported VIF table,
    following the project's diagnostic specification.
    """

    x = sample[PREDICTORS].astype(float).copy()

    rows = []

    for i, column in enumerate(x.columns):
        vif_value = variance_inflation_factor(
            x.values,
            i
        )

        rows.append({
            "Variable": column,
            "VIF": vif_value,
        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Breusch-Pagan test
# ---------------------------------------------------------------------

def calculate_breusch_pagan(model):
    """Run the Breusch-Pagan heteroskedasticity test."""

    residuals = model.resid
    exog = model.model.exog

    lm_stat, lm_pvalue, f_stat, f_pvalue = het_breuschpagan(
        residuals,
        exog
    )

    return {
        "BP_LM": lm_stat,
        "BP_p": lm_pvalue,
        "BP_F": f_stat,
        "BP_F_p": f_pvalue,
    }


# ---------------------------------------------------------------------
# Cook's distance
# ---------------------------------------------------------------------

def calculate_cooks_distance(model, sample):
    """Calculate Cook's distance and identify influential observations."""

    influence = OLSInfluence(model)

    cooks = influence.cooks_distance[0]

    threshold = 4 / len(sample)

    influential = cooks > threshold

    result = pd.DataFrame({
        "RIC": sample["RIC"].values,
        "Company_Name": sample["Company_Name"].values,
        "Cooks_Distance": cooks,
        "Influential_4_over_n": influential,
    })

    return {
        "table": result,
        "threshold": threshold,
        "count": int(influential.sum()),
        "maximum": float(np.max(cooks)),
    }


# ---------------------------------------------------------------------
# Sensitivity analysis
# ---------------------------------------------------------------------

def run_trimmed_model(data, outcome):
    """
    Re-estimate the model after trimming the dependent variable
    at the 1st and 99th percentiles.

    This is used as a sensitivity check for ROE and Tobin's Q.
    """

    required = [outcome, "GICS_Sector"] + PREDICTORS

    sample = data.dropna(subset=required).copy()

    lower = sample[outcome].quantile(0.01)
    upper = sample[outcome].quantile(0.99)

    trimmed = sample[
        (sample[outcome] >= lower)
        & (sample[outcome] <= upper)
    ].copy()

    x = make_design_matrix(trimmed)
    y = trimmed[outcome].astype(float)

    model = sm.OLS(y, x).fit(cov_type="HC3")

    coefficients = pd.DataFrame({
        "Variable": x.columns,
        "Coefficient": model.params.values,
        "HC3_SE": model.bse.values,
        "t": model.tvalues.values,
        "p": model.pvalues.values,
    })

    return model, coefficients, trimmed, lower, upper


# ---------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------

def main():

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} was not found. "
            "Place the licensed project dataset in the project folder."
        )

    OUTPUT_DIR.mkdir(exist_ok=True)

    data = load_data(DATA_FILE)

    print("=" * 80)
    print("BUSI1783 - Board Diversity and Firm Performance")
    print("=" * 80)

    print(f"Dataset rows: {len(data)}")
    print(f"Unique firms: {data['RIC'].nunique()}")

    # ---------------------------------------------------------------
    # Correlations
    # ---------------------------------------------------------------

    correlations = correlation_analysis(data)

    correlations.to_csv(
        OUTPUT_DIR / "correlations.csv"
    )

    print("\nPearson correlation matrix saved.")

    # ---------------------------------------------------------------
    # Main models
    # ---------------------------------------------------------------

    diagnostic_rows = []
    vif_tables = []
    coefficient_tables = []
    sensitivity_tables = []

    for outcome in OUTCOMES:

        print("\n" + "=" * 80)
        print(f"MAIN MODEL: {outcome}")
        print("=" * 80)

        model, coefficients, sample, x = run_ols(
            data,
            outcome
        )

        print(f"Complete-case N: {len(sample)}")
        print(f"R-squared: {model.rsquared:.6f}")
        print(f"Adjusted R-squared: {model.rsquared_adj:.6f}")

        print("\nCoefficients:")
        print(
            coefficients.to_string(
                index=False,
                float_format=lambda value: f"{value:.6f}"
            )
        )

        # Save coefficient table
        coefficient_table = coefficients.copy()
        coefficient_table.insert(0, "Outcome", outcome)
        coefficient_tables.append(coefficient_table)

        # -----------------------------------------------------------
        # VIF
        # -----------------------------------------------------------

        vif = calculate_vif(sample)

        vif.insert(0, "Outcome", outcome)
        vif_tables.append(vif)

        # -----------------------------------------------------------
        # Breusch-Pagan
        # -----------------------------------------------------------

        bp = calculate_breusch_pagan(model)

        # -----------------------------------------------------------
        # Cook's distance
        # -----------------------------------------------------------

        cooks = calculate_cooks_distance(
            model,
            sample
        )

        diagnostic_rows.append({
            "Outcome": outcome,
            "N": len(sample),
            "R_squared": model.rsquared,
            "Adjusted_R_squared": model.rsquared_adj,
            "BP_LM": bp["BP_LM"],
            "BP_p": bp["BP_p"],
            "BP_F": bp["BP_F"],
            "BP_F_p": bp["BP_F_p"],
            "Cook_threshold_4_over_n": cooks["threshold"],
            "Max_Cook": cooks["maximum"],
            "Influential_N": cooks["count"],
        })

        # Save Cook's distance table
        cooks["table"].to_csv(
            OUTPUT_DIR / f"{outcome}_cooks_distance.csv",
            index=False
        )

        print("\nDiagnostics:")
        print(f"Breusch-Pagan LM: {bp['BP_LM']:.6f}")
        print(f"Breusch-Pagan p-value: {bp['BP_p']:.6f}")
        print(f"Cook's 4/n threshold: {cooks['threshold']:.6f}")
        print(f"Maximum Cook's distance: {cooks['maximum']:.6f}")
        print(f"Influential observations: {cooks['count']}")

        # -----------------------------------------------------------
        # Sensitivity analysis
        # -----------------------------------------------------------

        if outcome in ["ROE", "Tobins_Q"]:

            (
                sensitivity_model,
                sensitivity_coefficients,
                trimmed,
                lower,
                upper,
            ) = run_trimmed_model(
                data,
                outcome
            )

            print("\nSensitivity analysis:")
            print(f"1st percentile: {lower:.6f}")
            print(f"99th percentile: {upper:.6f}")
            print(f"Trimmed N: {len(trimmed)}")
            print(
                f"Trimmed R-squared: "
                f"{sensitivity_model.rsquared:.6f}"
            )
            print(
                f"Trimmed adjusted R-squared: "
                f"{sensitivity_model.rsquared_adj:.6f}"
            )

            sensitivity_coefficients.insert(
                0,
                "Outcome",
                outcome
            )

            sensitivity_coefficients.insert(
                1,
                "Specification",
                "1%-99% trimmed"
            )

            sensitivity_tables.append(
                sensitivity_coefficients
            )

    # ---------------------------------------------------------------
    # Save combined output files
    # ---------------------------------------------------------------

    diagnostics = pd.DataFrame(diagnostic_rows)

    diagnostics.to_csv(
        OUTPUT_DIR / "diagnostics.csv",
        index=False
    )

    if coefficient_tables:
        pd.concat(
            coefficient_tables,
            ignore_index=True
        ).to_csv(
            OUTPUT_DIR / "regression_coefficients.csv",
            index=False
        )

    if vif_tables:
        pd.concat(
            vif_tables,
            ignore_index=True
        ).to_csv(
            OUTPUT_DIR / "vif.csv",
            index=False
        )

    if sensitivity_tables:
        pd.concat(
            sensitivity_tables,
            ignore_index=True
        ).to_csv(
            OUTPUT_DIR / "sensitivity_results.csv",
            index=False
        )

    # ---------------------------------------------------------------
    # Excel workbook
    # ---------------------------------------------------------------

    excel_file = OUTPUT_DIR / "BUSI1783_analysis_results.xlsx"

    with pd.ExcelWriter(
        excel_file,
        engine="openpyxl"
    ) as writer:

        data.describe(
            include="all"
        ).transpose().to_excel(
            writer,
            sheet_name="Descriptives"
        )

        correlations.to_excel(
            writer,
            sheet_name="Correlations"
        )

        diagnostics.to_excel(
            writer,
            sheet_name="Diagnostics",
            index=False
        )

        if coefficient_tables:
            pd.concat(
                coefficient_tables,
                ignore_index=True
            ).to_excel(
                writer,
                sheet_name="Coefficients",
                index=False
            )

        if vif_tables:
            pd.concat(
                vif_tables,
                ignore_index=True
            ).to_excel(
                writer,
                sheet_name="VIF",
                index=False
            )

        if sensitivity_tables:
            pd.concat(
                sensitivity_tables,
                ignore_index=True
            ).to_excel(
                writer,
                sheet_name="Sensitivity",
                index=False
            )

    print("\n" + "=" * 80)
    print("Analysis completed successfully.")
    print(f"Results saved to: {excel_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
