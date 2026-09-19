-- =============================================================
-- Case Study 2: Retail Sales & Customer Insights Dashboard
-- Phase 2: Data Warehouse Design & Development
-- File 1 of 3: CREATE - Database, Staging Tables, Star Schema
--              (Fact table + Dimension tables + Surrogate keys)
-- No data is loaded in this file - see 02_insert_data.sql for that.
-- =============================================================

CREATE DATABASE IF NOT EXISTS retail_dw;
USE retail_dw;

-- =============================================================
-- STAGING AREA
-- Raw landing tables that mirror the cleaned CSVs from Phase 1
-- (data/processed/sales_cleaned.csv, customers_cleaned.csv,
--  products_cleaned.csv). These are loaded first in 02_insert_data.sql,
-- then used as the source for the star schema INSERT...SELECT statements.
-- =============================================================

DROP TABLE IF EXISTS staging_sales;
CREATE TABLE staging_sales (
    SaleID              INT,           -- surrogate key (see Phase 1, 03_transform.py)
    OriginalSaleID      VARCHAR(50),   -- original alphanumeric SaleID (UUID), kept for traceability
    ProductID           INT,
    CustomerID          INT,           -- surrogate key (stripped "C0"/"C1" prefix)
    OriginalCustomerID  VARCHAR(10),   -- original alphanumeric CustomerID e.g. "C0460"
    SalesAmount         DECIMAL(10,2),
    Quantity            INT,
    `Timestamp`         DATETIME
);

DROP TABLE IF EXISTS staging_customer;
CREATE TABLE staging_customer (
    CustomerID          INT,
    OriginalCustomerID  VARCHAR(10),
    FirstName           VARCHAR(50),
    LastName             VARCHAR(50),
    Gender              VARCHAR(10),
    Region              VARCHAR(50),
    SSN                 VARCHAR(20)
);

DROP TABLE IF EXISTS staging_product;
CREATE TABLE staging_product (
    ProductID   INT,
    ProductName VARCHAR(100),
    Category    VARCHAR(50)
);

-- =============================================================
-- DATA WAREHOUSE (GOLD LAYER) - STAR SCHEMA
--
--   Fact Table  : fact_sales            (grain: one row per sale transaction)
--   Dimensions  : dim_customer, dim_product, dim_region
--
-- Surrogate keys used:
--   fact_sales.SaleID      -> INT surrogate (source SaleID is an alphanumeric
--                              UUID; the schema requires an INT primary key,
--                              so the surrogate generated in Phase 1 is used)
--   dim_customer.CustomerID -> INT surrogate (source CustomerID is
--                              alphanumeric, e.g. "C0460"; surrogate = the
--                              numeric part after stripping the "C0"/"C1"
--                              prefix, generated in Phase 1)
--   dim_product.ProductID   -> source ProductID was already numeric,
--                              reused as-is (no surrogate needed)
--   dim_region.RegionID     -> new AUTO_INCREMENT surrogate (Region had no
--                              ID at all in the source data)
-- =============================================================

-- -------------------------------------------------------------
-- Dimension: dim_region
-- -------------------------------------------------------------
DROP TABLE IF EXISTS dim_region;
CREATE TABLE dim_region (
    RegionID    INT AUTO_INCREMENT PRIMARY KEY,   -- surrogate key
    RegionName  VARCHAR(50) UNIQUE
);

-- -------------------------------------------------------------
-- Dimension: dim_customer
-- -------------------------------------------------------------
DROP TABLE IF EXISTS dim_customer;
CREATE TABLE dim_customer (
    CustomerID  INT PRIMARY KEY,        -- surrogate key
    FirstName   VARCHAR(50) NOT NULL,
    LastName    VARCHAR(50) NOT NULL,
    Gender      VARCHAR(10),
    RegionID    INT,                    -- FK -> dim_region
    SSN         VARCHAR(20) UNIQUE NOT NULL,
    FOREIGN KEY (RegionID) REFERENCES dim_region(RegionID)
);

-- -------------------------------------------------------------
-- Dimension: dim_product
-- -------------------------------------------------------------
DROP TABLE IF EXISTS dim_product;
CREATE TABLE dim_product (
    ProductID   INT PRIMARY KEY,        -- natural key, reused as-is
    ProductName VARCHAR(100) NOT NULL,
    Category    VARCHAR(50) NOT NULL
);

-- -------------------------------------------------------------
-- Fact: fact_sales
-- -------------------------------------------------------------
DROP TABLE IF EXISTS fact_sales;
CREATE TABLE fact_sales (
    SaleID       INT PRIMARY KEY,       -- surrogate key
    ProductID    INT,                   -- FK -> dim_product
    CustomerID   INT,                   -- FK -> dim_customer
    SalesAmount  DECIMAL(10,2) NOT NULL,
    Quantity     INT NOT NULL,
    `Timestamp`  DATETIME NOT NULL,
    FOREIGN KEY (ProductID)  REFERENCES dim_product(ProductID),
    FOREIGN KEY (CustomerID) REFERENCES dim_customer(CustomerID)
);

-- -------------------------------------------------------------
-- Confirm all tables were created
-- -------------------------------------------------------------
SHOW TABLES;
