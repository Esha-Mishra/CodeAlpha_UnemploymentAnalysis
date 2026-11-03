# CodeAlpha Task 2: Unemployment Analysis with Python
# Put this Python file in the same folder as both CSV files:
#   Unemployment in India.csv
#   Unemployment_Rate_upto_11_2020.csv

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

FILE1 = BASE_DIR / "Unemployment in India.csv"
FILE2 = BASE_DIR / "Unemployment_Rate_upto_11_2020.csv"

RATE = "Estimated Unemployment Rate (%)"
EMPLOYED = "Estimated Employed"
PARTICIPATION = "Estimated Labour Participation Rate (%)"


def load_and_clean(path, dataset_name):
    """Read a CSV, tidy column names, convert dates/numbers, remove unusable rows."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    # Remove fully empty rows and exact duplicate rows.
    df = df.dropna(how="all").drop_duplicates()

    # Convert date and numeric columns.
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(
            df["Date"].astype(str).str.strip(),
            dayfirst=True,
            errors="coerce"
        )

    for col in [RATE, EMPLOYED, PARTICIPATION]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # A record without date, region, or unemployment rate is not useful for this analysis.
    required = [c for c in ["Date", "Region", RATE] if c in df.columns]
    df = df.dropna(subset=required).copy()

    print(f"\n--- {dataset_name} ---")
    print("Rows and columns after cleaning:", df.shape)
    print("Date range:", df["Date"].min().date(), "to", df["Date"].max().date())
    print("Missing values after cleaning:\n", df.isna().sum())
    return df


def save_monthly_trend(df, filename, title):
    monthly = (
        df.assign(Month=df["Date"].dt.to_period("M").dt.to_timestamp())
          .groupby("Month")[RATE]
          .mean()
          .reset_index()
    )
    monthly.to_csv(OUTPUT_DIR / filename.replace(".png", ".csv"), index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(monthly["Month"], monthly[RATE], marker="o")
    plt.title(title)
    plt.xlabel("Month")
    plt.ylabel("Average unemployment rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=150)
    plt.close()
    return monthly


def main():
    # STEP 1: Load and clean BOTH files separately.
    # They have different structures: file 1 has Rural/Urban Area; file 2 has region coordinates.
    data1 = load_and_clean(FILE1, "Unemployment in India.csv")
    data2 = load_and_clean(FILE2, "Unemployment_Rate_upto_11_2020.csv")

    # STEP 2: Save cleaned versions so you can inspect them.
    data1.to_csv(OUTPUT_DIR / "cleaned_unemployment_india.csv", index=False)
    data2.to_csv(OUTPUT_DIR / "cleaned_unemployment_upto_nov2020.csv", index=False)

    # STEP 3: Explore summary statistics.
    print("\n=== Dataset 1: Overall unemployment summary ===")
    print(data1[RATE].describe().round(2))
    if "Area" in data1.columns:
        print("\nAverage unemployment rate by Area:")
        print(data1.groupby("Area")[RATE].mean().round(2))

    print("\n=== Dataset 2: Overall unemployment summary ===")
    print(data2[RATE].describe().round(2))

    # STEP 4: Plot unemployment trend from each dataset separately.
    monthly1 = save_monthly_trend(
        data1, "dataset1_monthly_trend.png",
        "Monthly Average Unemployment Rate (Dataset 1)"
    )
    monthly2 = save_monthly_trend(
        data2, "dataset2_monthly_trend.png",
        "Monthly Average Unemployment Rate (Dataset 2)"
    )

    # STEP 5: Compare Rural vs Urban, where Area is available (Dataset 1).
    if "Area" in data1.columns:
        area_avg = data1.groupby("Area")[RATE].mean().sort_values()
        area_avg.to_csv(OUTPUT_DIR / "average_rate_by_area.csv", header=["Average unemployment rate (%)"])
        plt.figure(figsize=(7, 5))
        area_avg.plot(kind="bar")
        plt.title("Average Unemployment Rate: Rural vs Urban")
        plt.xlabel("Area")
        plt.ylabel("Average unemployment rate (%)")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "rural_vs_urban.png", dpi=150)
        plt.close()

    # STEP 6: Examine the COVID-period pattern using Dataset 2.
    # The monthly average shows a sharp rise in April-May 2020 in this dataset.
    # This is an observed association, not proof that COVID alone caused every change.
    monthly2.to_csv(OUTPUT_DIR / "covid_period_monthly_summary.csv", index=False)
    plt.figure(figsize=(10, 5))
    plt.plot(monthly2["Month"], monthly2[RATE], marker="o")
    plt.axvline(pd.Timestamp("2020-03-01"), linestyle="--", label="COVID period reference (March 2020)")
    plt.title("Unemployment Trend During 2020 (Dataset 2)")
    plt.xlabel("Month")
    plt.ylabel("Average unemployment rate (%)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "covid_period_trend.png", dpi=150)
    plt.close()

    # STEP 7: Print key observations for your report.
    print("\n=== Key observations from the uploaded data ===")
    print("Dataset 1 monthly averages (%):")
    print(monthly1.assign(Month=monthly1["Month"].dt.strftime("%Y-%m")).round(2).to_string(index=False))
    print("\nDataset 2 monthly averages (%):")
    print(monthly2.assign(Month=monthly2["Month"].dt.strftime("%Y-%m")).round(2).to_string(index=False))

    if "Area" in data1.columns:
        area_avg = data1.groupby("Area")[RATE].mean().round(2)
        print("\nArea comparison (%):")
        print(area_avg.to_string())

    print("\nFiles saved in:", OUTPUT_DIR)
    print("Open the 'outputs' folder to see the cleaned CSVs, summary CSVs, and graphs.")


if __name__ == "__main__":
    main()
