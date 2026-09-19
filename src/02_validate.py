"""
Case Study 2: Retail Sales & Customer Insights Dashboard
Phase 1: Data Warehouse Design & Development
Step 2 of 4 - VALIDATE

Reads the extracted layer and runs a full data quality audit:
    - Null value analysis
    - Duplicate row check
    - Duplicate primary key validation
    - Referential integrity check (sales -> customers, sales -> products)

This script does NOT modify any data - it only reports issues that
03_transform.py will then resolve using documented business rules.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STAGING_DIR = os.path.join(BASE_DIR, "..", "data", "staging")

sales_df = pd.read_csv(f"{STAGING_DIR}/sales_extracted.csv")
customers_df = pd.read_csv(f"{STAGING_DIR}/customers_extracted.csv")
products_df = pd.read_csv(f"{STAGING_DIR}/products_extracted.csv")

tables = {"Sales": sales_df, "Customers": customers_df, "Products": products_df}

# ---------------------------------------------------------------------------
# 1. Null Value Analysis
# ---------------------------------------------------------------------------
print("=" * 60)
print("NULL VALUE ANALYSIS")
print("=" * 60)
for name, df in tables.items():
    print(f"\n{name} Table - Null Values:")
    print(df.isnull().sum())
    print("Total Nulls:", df.isnull().sum().sum())

# ---------------------------------------------------------------------------
# 2. Duplicate Row Check
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("DUPLICATE ROW CHECK")
print("=" * 60)
for name, df in tables.items():
    print(f"{name} Table - Full Duplicate Rows:", df.duplicated().sum())

# ---------------------------------------------------------------------------
# 3. Duplicate Primary Key Validation
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("DUPLICATE PRIMARY KEY VALIDATION")
print("=" * 60)
print("Duplicate SaleID:", sales_df["saleid"].duplicated().sum())
print("Duplicate CustomerID (raw):", customers_df["customerid"].duplicated().sum())
print("Duplicate ProductID:", products_df["productid"].duplicated().sum())

# ---------------------------------------------------------------------------
# 4. Referential Integrity Check
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("REFERENTIAL INTEGRITY CHECK")
print("=" * 60)
orphan_customers = set(sales_df["customerid"]) - set(customers_df["customerid"])
orphan_products = set(sales_df["productid"]) - set(products_df["productid"])
print(f"Sales rows referencing a CustomerID not in Customers table: {len(orphan_customers)}")
print(f"Sales rows referencing a ProductID not in Products table:  {len(orphan_products)}")

# ---------------------------------------------------------------------------
# 5. Business-key format check (for the surrogate key rule)
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("ID FORMAT CHECK (for surrogate key generation in Transform step)")
print("=" * 60)
print("Sample sale_id values (kept as-is, alphanumeric):", sales_df["saleid"].head(3).tolist())
print("Sample customer_id prefixes:", sales_df["customerid"].str[:2].unique())

print("\nValidation complete. See 03_transform.py for how each issue above is resolved.")
