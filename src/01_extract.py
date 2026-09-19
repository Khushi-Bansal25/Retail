"""
Case Study 2: Retail Sales & Customer Insights Dashboard
Phase 1: Data Warehouse Design & Development
Step 1 of 4 - EXTRACT

Sources (as identified in the project brief):
    - Sales Data    -> MySQL       -> data/raw/sales_1.csv
    - Customer Data -> NoSQL       -> data/raw/customers.json
    - Product Data  -> SharePoint  -> data/raw/products.csv

This script only extracts and standardizes structure (column names,
duplicate columns). It does NOT clean values yet - that happens in
03_transform.py. Output goes to data/staging/ as the "extracted" layer.
"""

import pandas as pd
import os

# Paths are resolved relative to THIS file's location, not the current
# working directory - so this script runs correctly whether you launch it
# from the src/ folder, the project root, or VS Code's Run button.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
STAGING_DIR = os.path.join(BASE_DIR, "..", "data", "staging")

# ---------------------------------------------------------------------------
# 1. Data Extraction
# ---------------------------------------------------------------------------
sales_df = pd.read_csv(f"{RAW_DIR}/sales_1.csv")
customers_df = pd.read_json(f"{RAW_DIR}/customers.json")
products_df = pd.read_csv(f"{RAW_DIR}/products.csv")

print("Data Loaded Successfully")
print(f"sales_df:     {sales_df.shape}")
print(f"customers_df: {customers_df.shape}")
print(f"products_df:  {products_df.shape}\n")

# ---------------------------------------------------------------------------
# 2. Column Name Standardization
# ---------------------------------------------------------------------------
def normalize_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df

sales_df = normalize_columns(sales_df)
customers_df = normalize_columns(customers_df)
products_df = normalize_columns(products_df)

print("Column names normalized.")
print("sales columns:", list(sales_df.columns))
print("customers columns:", list(customers_df.columns))
print("products columns:", list(products_df.columns), "\n")

# ---------------------------------------------------------------------------
# 3. Handling Duplicate Column Names
# ---------------------------------------------------------------------------
def handle_duplicate_columns(df):
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        duplicate_indexes = cols[cols == dup].index.tolist()
        for i in range(1, len(duplicate_indexes)):
            cols[duplicate_indexes[i]] = f"{dup}_{i}"
    df.columns = cols
    return df

sales_df = handle_duplicate_columns(sales_df)
customers_df = handle_duplicate_columns(customers_df)
products_df = handle_duplicate_columns(products_df)

print("Duplicate column names checked (none found in this dataset).\n")

# ---------------------------------------------------------------------------
# 4. Save extracted (structure-only) layer for the next step
# ---------------------------------------------------------------------------
sales_df.to_csv(f"{STAGING_DIR}/sales_extracted.csv", index=False)
customers_df.to_csv(f"{STAGING_DIR}/customers_extracted.csv", index=False)
products_df.to_csv(f"{STAGING_DIR}/products_extracted.csv", index=False)

print("Extraction complete. Files saved to data/staging/:")
print("  sales_extracted.csv, customers_extracted.csv, products_extracted.csv")
