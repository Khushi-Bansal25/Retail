-- =============================================================
-- Case Study 2: Retail Sales & Customer Insights Dashboard
-- Phase 3: Data Analysis & SQL Implementation
-- File 3 of 3: KPI Queries
-- Run against retail_dw (fact_sales, dim_customer, dim_product, dim_region)
-- =============================================================
USE retail_dw;

-- -------------------------------------------------------------
-- QUERY DEVELOPMENT
-- -------------------------------------------------------------

-- 1. Identify best-selling / top-performing products (by revenue and units)
SELECT
    p.ProductName,
    p.Category,
    SUM(f.SalesAmount) AS total_revenue,
    SUM(f.Quantity)    AS total_units_sold
FROM fact_sales f
JOIN dim_product p ON f.ProductID = p.ProductID
GROUP BY p.ProductName, p.Category
ORDER BY total_revenue DESC
LIMIT 10;

-- 2. Segment customers based on purchase patterns
--    (Frequency = number of purchases, Monetary = total spend)
SELECT
    c.CustomerID, c.FirstName, c.LastName,
    COUNT(*)            AS purchase_frequency,
    SUM(f.SalesAmount)  AS total_spend,
    CASE
        WHEN SUM(f.SalesAmount) >= 20000 THEN 'High Value'
        WHEN SUM(f.SalesAmount) >= 8000  THEN 'Medium Value'
        ELSE 'Low Value'
    END AS customer_segment
FROM fact_sales f
JOIN dim_customer c ON f.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY total_spend DESC;

-- 3. Analyze regional sales trends
SELECT
    r.RegionName,
    COUNT(*)                     AS num_transactions,
    SUM(f.SalesAmount)           AS region_revenue,
    ROUND(AVG(f.SalesAmount), 2) AS avg_transaction_value
FROM fact_sales f
JOIN dim_customer c ON f.CustomerID = c.CustomerID
JOIN dim_region r   ON c.RegionID = r.RegionID
GROUP BY r.RegionName
ORDER BY region_revenue DESC;

-- 4. Seasonality - sales by month across the full dataset
--    (helps spot which months/seasons drive the most revenue)
SELECT
    MONTH(f.Timestamp)     AS month_number,
    MONTHNAME(f.Timestamp) AS month_name,
    COUNT(*)               AS num_transactions,
    SUM(f.SalesAmount)     AS monthly_revenue
FROM fact_sales f
GROUP BY MONTH(f.Timestamp), MONTHNAME(f.Timestamp)
ORDER BY month_number;

-- -------------------------------------------------------------
-- KPI CALCULATION - SALES PERFORMANCE
-- -------------------------------------------------------------

-- 5. Total Sales Revenue
SELECT ROUND(SUM(SalesAmount), 2) AS total_sales_revenue
FROM fact_sales;

-- 6. Sales Growth Rate - Monthly
WITH monthly AS (
    SELECT YEAR(Timestamp) AS yr, MONTH(Timestamp) AS mo,
           SUM(SalesAmount) AS monthly_revenue
    FROM fact_sales
    GROUP BY YEAR(Timestamp), MONTH(Timestamp)
)
SELECT yr, mo, monthly_revenue,
       ROUND(
           (monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY yr, mo))
           / LAG(monthly_revenue) OVER (ORDER BY yr, mo) * 100, 2
       ) AS growth_rate_pct
FROM monthly
ORDER BY yr, mo;

-- 6b. Sales Growth Rate - Quarterly
WITH quarterly AS (
    SELECT YEAR(Timestamp) AS yr, QUARTER(Timestamp) AS qtr,
           SUM(SalesAmount) AS quarterly_revenue
    FROM fact_sales
    GROUP BY YEAR(Timestamp), QUARTER(Timestamp)
)
SELECT yr, qtr, quarterly_revenue,
       ROUND(
           (quarterly_revenue - LAG(quarterly_revenue) OVER (ORDER BY yr, qtr))
           / LAG(quarterly_revenue) OVER (ORDER BY yr, qtr) * 100, 2
       ) AS growth_rate_pct
FROM quarterly
ORDER BY yr, qtr;

-- 6c. Sales Growth Rate - Yearly
WITH yearly AS (
    SELECT YEAR(Timestamp) AS yr, SUM(SalesAmount) AS yearly_revenue
    FROM fact_sales
    GROUP BY YEAR(Timestamp)
)
SELECT yr, yearly_revenue,
       ROUND(
           (yearly_revenue - LAG(yearly_revenue) OVER (ORDER BY yr))
           / LAG(yearly_revenue) OVER (ORDER BY yr) * 100, 2
       ) AS growth_rate_pct
FROM yearly
ORDER BY yr;

-- 7. Average Transaction Value (ATV)
SELECT ROUND(AVG(SalesAmount), 2) AS avg_transaction_value
FROM fact_sales;

-- 8. Sales by Product Category
SELECT
    p.Category,
    ROUND(SUM(f.SalesAmount), 2) AS category_revenue,
    ROUND(SUM(f.SalesAmount) * 100.0 / (SELECT SUM(SalesAmount) FROM fact_sales), 2) AS pct_of_total
FROM fact_sales f
JOIN dim_product p ON f.ProductID = p.ProductID
GROUP BY p.Category
ORDER BY category_revenue DESC;

-- 9. Sales by Region (Regional Sales Performance)
SELECT
    r.RegionName,
    ROUND(SUM(f.SalesAmount), 2) AS region_revenue,
    COUNT(*) AS num_transactions
FROM fact_sales f
JOIN dim_customer c ON f.CustomerID = c.CustomerID
JOIN dim_region r   ON c.RegionID = r.RegionID
GROUP BY r.RegionName
ORDER BY region_revenue DESC;

-- -------------------------------------------------------------
-- KPI CALCULATION - CUSTOMER INSIGHTS
-- -------------------------------------------------------------

-- 10. Customer Lifetime Value (CLV) - Top 10 customers
SELECT
    c.CustomerID, c.FirstName, c.LastName,
    ROUND(SUM(f.SalesAmount), 2) AS lifetime_value,
    COUNT(*) AS num_purchases
FROM fact_sales f
JOIN dim_customer c ON f.CustomerID = c.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY lifetime_value DESC
LIMIT 10;

-- 10b. Average CLV across all customers
SELECT ROUND(AVG(customer_total), 2) AS avg_clv
FROM (
    SELECT CustomerID, SUM(SalesAmount) AS customer_total
    FROM fact_sales
    GROUP BY CustomerID
) t;

-- 11. Customer Demographics Analysis (Gender + Region breakdown)
SELECT
    c.Gender,
    r.RegionName,
    COUNT(DISTINCT c.CustomerID) AS num_customers,
    ROUND(SUM(f.SalesAmount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c ON f.CustomerID = c.CustomerID
JOIN dim_region r   ON c.RegionID = r.RegionID
GROUP BY c.Gender, r.RegionName
ORDER BY c.Gender, total_revenue DESC;

-- -------------------------------------------------------------
-- KPI CALCULATION - PRODUCT PERFORMANCE
-- -------------------------------------------------------------

-- 12. Top-Selling Products (same as Query 1, repeated here under its KPI name)
SELECT
    p.ProductName, p.Category,
    SUM(f.SalesAmount) AS total_revenue,
    SUM(f.Quantity)    AS total_units_sold
FROM fact_sales f
JOIN dim_product p ON f.ProductID = p.ProductID
GROUP BY p.ProductName, p.Category
ORDER BY total_revenue DESC
LIMIT 10;

-- -------------------------------------------------------------
-- NOTE - Metrics requested that CANNOT be calculated from the
-- current dataset (flagging rather than fabricating numbers):
--
--   - Product Return Rate : no "Returns"/"IsReturned" field exists
--     in sales_1.csv. Needs a returns table or a return flag column.
--
--   - Cost of Goods Sold (COGS) : no unit cost / COGS field exists
--     in products.csv. Needs a "UnitCost" column to compute COGS
--     or gross margin.
--
--   - Promotions (as part of "Understanding Complex Purchasing
--     Patterns") : no promotions/discount field exists anywhere in
--     the source data. Seasonality (query 4 above) and Customer
--     Demographics (query 11 above) ARE covered from what's
--     available; Promotions is not.
--
-- If a returns log, a product cost file, or a promotions file
-- becomes available, send it over and I'll add these queries.
-- -------------------------------------------------------------
