"""
Case Study 2: Retail Sales & Customer Insights Dashboard
Phase 1: Data Warehouse Design & Development
Step 3 of 4 - TRANSFORM

Resolves every issue flagged by 02_validate.py using documented
business rules, and builds the surrogate keys required by the
target schema (Sales.SaleID INT PK, Sales.CustomerID INT FK).
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STAGING_DIR = os.path.join(BASE_DIR, "..", "data", "staging")

sales_df = pd.read_csv(f"{STAGING_DIR}/sales_extracted.csv")
customers_df = pd.read_csv(f"{STAGING_DIR}/customers_extracted.csv")
products_df = pd.read_csv(f"{STAGING_DIR}/products_extracted.csv")

# ---------------------------------------------------------------------------
# 1. Customers - remove exact duplicate rows
#    (all 100 duplicate CustomerIDs found in validation were full-row
#    duplicates, so a safe drop resolves the primary key violation)
# ---------------------------------------------------------------------------
customers_df = customers_df.drop_duplicates(subset=["customerid"]).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 2. Customers - standardize Gender
# ---------------------------------------------------------------------------
customers_df["gender"] = (
    customers_df["gender"]
    .str.strip()
    .str.lower()
    .map({"m": "Male", "male": "Male", "f": "Female", "female": "Female"})
)

# ---------------------------------------------------------------------------
# 3. Customers - standardize Region (fix typos / casing / abbreviations)
# ---------------------------------------------------------------------------
region_map = {
    "ohho": "Ohio", "ohio": "Ohio",
    "new yorkk": "New York", "new york": "New York", "nw york": "New York", "ny": "New York",
    "california": "California", "californiya": "California",
    "texas": "Texas", "texaz": "Texas",
}
customers_df["region"] = (
    customers_df["region"]
    .str.strip()
    .str.lower()
    .map(region_map)
    .fillna("Unknown")
)

# ---------------------------------------------------------------------------
# 4. Customers - handle missing last names
# ---------------------------------------------------------------------------
customers_df["lastname"] = customers_df["lastname"].fillna("Unknown")

print("Customer cleaning complete.")
print("  Gender values:", customers_df["gender"].unique())
print("  Region values:", customers_df["region"].unique())

# ---------------------------------------------------------------------------
# 5. Sales - handle missing SalesAmount / Quantity
#    Business rule:
#      - Both missing  -> row unusable, drop
#      - Quantity only missing -> impute with product's median quantity
#      - SalesAmount only missing -> impute using product's median unit
#        price (salesamount / quantity) * this row's quantity
# ---------------------------------------------------------------------------
sales_df["unit_price"] = sales_df["salesamount"] / sales_df["quantity"]
median_unit_price = sales_df.groupby("productid")["unit_price"].median()
median_quantity = sales_df.groupby("productid")["quantity"].median()

both_missing = sales_df["salesamount"].isna() & sales_df["quantity"].isna()
print(f"\nRows with both salesamount and quantity missing (dropped): {both_missing.sum()}")
sales_df = sales_df[~both_missing].copy()

missing_qty = sales_df["quantity"].isna()
sales_df.loc[missing_qty, "quantity"] = sales_df.loc[missing_qty, "productid"].map(median_quantity)

missing_amt = sales_df["salesamount"].isna()
sales_df.loc[missing_amt, "salesamount"] = (
    sales_df.loc[missing_amt, "productid"].map(median_unit_price)
    * sales_df.loc[missing_amt, "quantity"]
)

sales_df["quantity"] = sales_df["quantity"].round().astype(int)
sales_df["salesamount"] = sales_df["salesamount"].round(2)
sales_df.drop(columns=["unit_price"], inplace=True)

print("Remaining nulls in sales_df:\n", sales_df.isnull().sum())

# ---------------------------------------------------------------------------
# 6. Surrogate Key Generation
#    Target schema requires SaleID INT PRIMARY KEY and CustomerID INT.
#    Source IDs are alphanumeric, so:
#      - sale_id   -> kept AS-IS (original UUID, business/tracking key)
#      - sale_key  -> NEW surrogate int, this becomes the schema's "SaleID"
#      - customer_id -> kept AS-IS in both tables
#      - customer_key -> strip leading 2 chars ("C0"/"C1") + cast to int,
#                         this becomes the schema's "CustomerID"
# ---------------------------------------------------------------------------
sales_df = sales_df.reset_index(drop=True)
sales_df.insert(0, "sale_key", sales_df.index + 1)
sales_df["customer_key"] = sales_df["customerid"].str[2:].astype(int)
customers_df["customer_key"] = customers_df["customerid"].str[2:].astype(int)

sales_df["timestamp"] = pd.to_datetime(sales_df["timestamp"])

print("\nSurrogate keys created: sale_key, customer_key")

# ---------------------------------------------------------------------------
# 7. Save transformed layer
# ---------------------------------------------------------------------------
sales_df.to_csv(f"{STAGING_DIR}/sales_transformed.csv", index=False)
customers_df.to_csv(f"{STAGING_DIR}/customers_transformed.csv", index=False)
products_df.to_csv(f"{STAGING_DIR}/products_transformed.csv", index=False)

print("\nTransform complete. Files saved to data/staging/:")
print("  sales_transformed.csv, customers_transformed.csv, products_transformed.csv")
