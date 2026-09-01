from pathlib import Path
from math import erf, sqrt
import numpy as np
import pandas as pd

DATA_FILE = Path("BUSI1783_Cross_Sectional_Dataset.xlsx")


def normalise_name(value):
    return " ".join(str(value).replace("\n", " ").split()).strip().lower()


def load_data(file_path):
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

    if "Policy_Experience" in df.columns:
        values = (
            df["Policy_Experience"]
            .astype(str)
            .str.strip()
            .str.lower()
        )
        df["Policy_Experience"] = values.map({
            "true": 1,
            "false": 0,
            "1": 1,
            "0": 0
        })

    return df


def ols_hc3(X, y):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    n, k = X.shape
    xtx_inv = np.linalg.pinv(X.T @ X)

    beta = xtx_inv @ X.T @ y
    fitted = X @ beta
    residuals = y - fitted

    hat = np.sum((X @ xtx_inv) * X, axis=1)
    adjustment = np.maximum(1.0 - hat, 1e-12)

    scaled = (residuals / adjustment) ** 2
    meat = X.T @ (X * scaled[:, None])
    covariance = xtx_inv @ meat @ xtx_inv

    se = np.sqrt(np.maximum(np.diag(covariance), 0))
    t_values = beta / np.where(se == 0, np.nan, se)

    p_values = np.array([
        1 - erf(abs(t) / sqrt(2))
        if np.isfinite(t) else np.nan
        for t in t_values
    ])

    sse = np.sum(residuals ** 2)
    sst = np.sum((y - np.mean(y)) ** 2)

    r_squared = 1 - sse / sst if sst != 0 else np.nan
    adjusted_r_squared = (
        1 - (1 - r_squared) * (n - 1) / (n - k)
        if n > k else np.nan
    )

    return {
        "beta": beta,
        "se": se,
        "t": t_values,
        "p": p_values,
        "residuals": residuals,
        "fitted": fitted,
        "hat": hat,
        "r_squared": r_squared,
        "adjusted_r_squared": adjusted_r_squared,
        "n": n,
        "k": k,
    }


def make_design_matrix(data):
    predictors = [
        "Gender_Diversity",
        "Specific_Skills",
        "Policy_Experience",
        "Board_Size",
        "Firm_Size",
        "Leverage",
    ]

    x = data[predictors].astype(float).copy()

    sector_dummies = pd.get_dummies(
        data["GICS_Sector"].astype(str),
        prefix="Sector",
        drop_first=True,
        dtype=float,
    )

    x = pd.concat([x, sector_dummies], axis=1)
    x.insert(0, "Intercept", 1.0)

    return x


def run_model(data, outcome):
    predictors = [
        "Gender_Diversity",
        "Specific_Skills",
        "Policy_Experience",
        "Board_Size",
        "Firm_Size",
        "Leverage",
    ]

    required = [outcome, "GICS_Sector"] + predictors
    sample = data.dropna(subset=required).copy()

    x = make_design_matrix(sample)
    y = sample[outcome].astype(float)

    result = ols_hc3(x.to_numpy(), y.to_numpy())

    table = pd.DataFrame({
        "Variable": x.columns,
        "Coefficient": result["beta"],
        "HC3_SE": result["se"],
        "t": result["t"],
        "p": result["p"],
    })

    return result, table, sample


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"{DATA_FILE} was not found in the project folder."
        )

    data = load_data(DATA_FILE)

    print("Dataset shape:", data.shape)
    print("Unique firms:", data["RIC"].nunique())

    for outcome in ["ROA", "ROE", "Tobins_Q"]:
        result, table, sample = run_model(data, outcome)

        print("\n" + "=" * 70)
        print(outcome)
        print("=" * 70)
        print("Complete-case N:", result["n"])
        print("R-squared:", result["r_squared"])
        print("Adjusted R-squared:", result["adjusted_r_squared"])
        print(table.to_string(index=False))


if __name__ == "__main__":
    main()
