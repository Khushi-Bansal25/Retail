"""
Case Study 2: Retail Sales & Customer Insights Dashboard
Phase 1: Data Warehouse Design & Development
Step 4 of 4 - LOAD (preparation)

Maps the transformed data onto the EXACT target schema columns
(as specified in the project schema: Sales/Customer/Product tables)
and writes the final "load-ready" CSVs to data/processed/.

These files are what 01_create_and_load_star_schema.sql (in ../sql/)
loads into MySQL via LOAD DATA INFILE.

Target schema recap:
  Sales     : SaleID (INT PK), ProductID (INT FK), CustomerID (INT FK),
              SalesAmount (DECIMAL(10,2)), Quantity (INT), Timestamp (DATETIME)
  Customer  : CustomerID (INT PK), FirstName, LastName, Gender, Region, SSN
  Product   : ProductID (INT PK), ProductName, Category

Note: SaleID/CustomerID in the schema are INT, but the source systems use
alphanumeric IDs ("C0460", UUIDs). The surrogate keys built in
03_transform.py (sale_key, customer_key) satisfy the INT requirement and
are used here as SaleID/CustomerID. The original alphanumeric values are
kept alongside as OriginalSaleID/OriginalCustomerID for traceability -
drop those two columns before loading if you want an exact 1:1 schema match.
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STAGING_DIR = os.path.join(BASE_DIR, "..", "data", "staging")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "data", "processed")

sales_df = pd.read_csv(f"{STAGING_DIR}/sales_transformed.csv", parse_dates=["timestamp"])
customers_df = pd.read_csv(f"{STAGING_DIR}/customers_transformed.csv")
products_df = pd.read_csv(f"{STAGING_DIR}/products_transformed.csv")

# ---------------------------------------------------------------------------
# Sales -> target schema columns
# ---------------------------------------------------------------------------
sales_final = sales_df.rename(columns={
    "sale_key": "SaleID",
    "saleid": "OriginalSaleID",
    "productid": "ProductID",
    "customer_key": "CustomerID",
    "customerid": "OriginalCustomerID",
    "salesamount": "SalesAmount",
    "quantity": "Quantity",
    "timestamp": "Timestamp",
})[[
    "SaleID", "OriginalSaleID", "ProductID", "CustomerID",
    "OriginalCustomerID", "SalesAmount", "Quantity", "Timestamp"
]]

# ---------------------------------------------------------------------------
# Customer -> target schema columns
# ---------------------------------------------------------------------------
customers_final = customers_df.rename(columns={
    "customer_key": "CustomerID",
    "customerid": "OriginalCustomerID",
    "firstname": "FirstName",
    "lastname": "LastName",
    "gender": "Gender",
    "region": "Region",
    "ssn": "SSN",
})[[
    "CustomerID", "OriginalCustomerID", "FirstName", "LastName",
    "Gender", "Region", "SSN"
]]

# ---------------------------------------------------------------------------
# Product -> target schema columns
# ---------------------------------------------------------------------------
products_final = products_df.rename(columns={
    "productid": "ProductID",
    "productname": "ProductName",
    "category": "Category",
})[["ProductID", "ProductName", "Category"]]

# ---------------------------------------------------------------------------
# Save load-ready files
# ---------------------------------------------------------------------------
sales_final.to_csv(f"{PROCESSED_DIR}/sales_cleaned.csv", index=False)
customers_final.to_csv(f"{PROCESSED_DIR}/customers_cleaned.csv", index=False)
products_final.to_csv(f"{PROCESSED_DIR}/products_cleaned.csv", index=False)

print("Load preparation complete. Files saved to data/processed/:")
print(f"  sales_cleaned.csv     : {sales_final.shape}")
print(f"  customers_cleaned.csv : {customers_final.shape}")
print(f"  products_cleaned.csv  : {products_final.shape}")
print("\nThese are now ready for LOAD DATA INFILE in MySQL Workbench")
print("(see ../sql/01_create_and_load_star_schema.sql)")
