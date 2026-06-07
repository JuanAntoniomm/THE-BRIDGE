"""
This script retrieves electricity data from the ENTSO-E Transparency Platform.
"""

from dotenv import dotenv_values
from entsoe import EntsoePandasClient
import pandas as pd
from datetime import datetime


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

config = dotenv_values(".env")
ENTSOE_API_KEY = config["ENTSOE_API_KEY"]

COUNTRY = "ES"  # Spain
TZ = "Europe/Madrid"

# Date range
START = pd.Timestamp("2024-01-01", tz=TZ)
END   = pd.Timestamp("2025-09-01", tz=TZ)

# ---------------------------------------------------------
# INITIALIZE CLIENT
# ---------------------------------------------------------

client = EntsoePandasClient(api_key=ENTSOE_API_KEY)

# ---------------- 1. TOTAL GENERATION ----------------

print("Downloading total generation for Spain...")

gen_df = client.query_generation(
    country_code=COUNTRY,
    start=START,
    end=END
)

gen_df.columns = gen_df.columns.droplevel(1)

# ---------------- 2. CROSS-BORDER FLOWS ----------------

print("Downloading cross-border flows...")

def get_flow(from_c, to_c):
    try:
        s = client.query_crossborder_flows(
            country_code_from=from_c,
            country_code_to=to_c,
            start=START,
            end=END
        )
        return s
    except Exception as e:
        print(f"Warning: no flow data for {from_c}->{to_c}: {e}")
        return pd.Series(dtype=float)

flows = pd.DataFrame({
    "flow_es_fr": get_flow("ES", "FR"),
    "flow_fr_es": get_flow("FR", "ES"),
    "flow_es_pt": get_flow("ES", "PT"),
    "flow_pt_es": get_flow("PT", "ES")
})

# ---------------- 3. DAY-AHEAD PRICES ----------------

print("Downloading day-ahead prices for Spain...")

prices = client.query_day_ahead_prices(
    country_code=COUNTRY,
    start=START,
    end=END
).rename("day_ahead_price")

# ---------------- 4. MERGE ALL DATA ----------------

print("Merging datasets...")

df = gen_df.join(flows, how="outer").join(prices, how="outer")
df = df.resample("D").mean()

# with data

df = df.iloc[:,[0,3,4,5,9,10,11,12,14,15,16,17,18,20,21,22,23,24,25]]

# ---------------- 5. OUTPUT ----------------

print("\nPreview:")
print(df.head())

output_file = "entsoe_spain.csv"
df.to_csv(output_file)
print(f"\nSaved to {output_file}")
