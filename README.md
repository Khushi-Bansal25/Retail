# Retail Sales & Customer Insights Dashboard

An end-to-end data analytics project that integrates sales, customer, and product data from three separate sources into a MySQL star-schema data warehouse, and presents the results through an interactive Power BI dashboard.

## Project Overview

This project follows a five-phase pipeline:

1. **Data Extraction, Cleaning and Preprocessing** (Python) — raw data from three sources is extracted, validated, cleaned, and prepared for warehouse loading.
2. **Star Schema Design and Development** (SQL / MySQL) — cleaned data is loaded into a normalized star schema: one fact table and three dimension tables.
3. **SQL-Based KPI Implementation** — business KPIs (revenue, growth rate, customer lifetime value, segmentation, regional trends, and more) are calculated directly against the warehouse.
4. **Power BI Data Modeling** — the same star schema is rebuilt in Power BI with a full library of DAX measures.
5. **Power BI Dashboard Development** — a four-page interactive dashboard covering Sales Performance, Customer Insights, Product & Regional analysis, and an Executive Summary.

## Data Sources

| Source | Format | Description |
|---|---|---|
| Sales Data | `sales_1.csv` | Transactional sales records |
| Customer Data | `customers.json` | Customer demographic records |
| Product Data | `products.csv` | Product catalog |

## Folder Structure

```
Retail/
├── data/
│   ├── raw/          # Original source files (not tracked in Git)
│   ├── staging/       # Intermediate extract/transform outputs (not tracked in Git)
│   └── processed/     # Final cleaned, load-ready CSVs
├── src/
│   ├── 01_extract.py     # Extract: load raw sources, standardize structure
│   ├── 02_validate.py    # Validate: data quality audit (read-only)
│   ├── 03_transform.py   # Transform: apply business-rule cleaning
│   └── 04_load.py        # Load: map to target schema, write load-ready files
├── sql/
│   ├── 01_create_tables.sql   # Star schema DDL (staging + gold layer)
│   ├── 02_insert_data.sql     # Data load into staging and gold layer
│   └── 03_kpi_queries.sql     # All KPI queries
├── powerbi/
│   ├── Dim_Region.csv
│   ├── Dim_Customer.csv
│   ├── Dim_Product.csv
│   ├── Fact_Sales.csv
│   └── dax_measures_table.dax   # Full DAX measures library
└── README.md
```

## How to Run

### Phase 1 — Python ETL
From inside the `src/` folder (or the project root — paths are resolved automatically):
```bash
python 01_extract.py
python 02_validate.py
python 03_transform.py
python 04_load.py
```
This produces the final cleaned files in `data/processed/`.

### Phase 2 & 3 — SQL Warehouse and KPIs
Run in MySQL Workbench, in this order:
1. `sql/01_create_tables.sql` — creates the database and all tables
2. `sql/02_insert_data.sql` — loads the cleaned data and populates the star schema
3. `sql/03_kpi_queries.sql` — runs all KPI queries

### Phase 4 & 5 — Power BI
1. Open Power BI Desktop
2. Get Data → Text/CSV → import all four files from `powerbi/`
3. Build relationships in Model view: `Dim_Region → Dim_Customer → Fact_Sales ← Dim_Product`
4. Create a dedicated `_Measures` table and add each measure from `powerbi/dax_measures_table.dax`
5. Build the dashboard pages using the measures and relationships above

## Star Schema

- **Fact Table:** `fact_sales` (grain: one row per sales transaction)
- **Dimension Tables:** `dim_customer`, `dim_product`, `dim_region`

## Key KPIs Implemented

- Total Sales Revenue, Average Transaction Value
- Sales Growth Rate (Monthly / Quarterly / Yearly)
- Sales by Product Category, Sales by Region
- Customer Lifetime Value, Customer Demographics
- Best-Selling Products, Customer Segmentation
- Seasonality (monthly revenue trend)

**Not calculable from the available source data** (documented, not fabricated): Product Return Rate, Cost of Goods Sold (COGS), and Promotions — none of the three source files contain a returns flag, unit-cost field, or promotions field.

## Tech Stack

- **Python** (pandas) — data cleaning and transformation
- **MySQL** — data warehouse
- **Power BI Desktop** — data modeling and dashboard
- **DAX** — measures and calculated columns

## Author

Khushi Bansal
