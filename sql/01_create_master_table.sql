-- =====================================================================
-- Banking Transactions Master Analytical Table (OBT)
-- Storage Engine: DuckDB / Columnar Parquet
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

CREATE TABLE IF NOT EXISTS warehouse.banking_transactions_master (
    transaction_id       VARCHAR(64) PRIMARY KEY,
    customer_id          VARCHAR(32) NOT NULL,
    customer_name        VARCHAR(100),
    customer_segment     VARCHAR(20),       -- Retail, Premium, Corporate
    account_id           VARCHAR(32) NOT NULL,
    account_type         VARCHAR(20) NOT NULL,       -- Checking, Savings, Credit
    branch_code          VARCHAR(10) NOT NULL,
    transaction_time     TIMESTAMP NOT NULL,
    transaction_date     DATE NOT NULL,
    transaction_type     VARCHAR(20) NOT NULL,       -- DEBIT, CREDIT, TRANSFER
    category             VARCHAR(50) NOT NULL,       -- Wire, Payroll, Retail, Utility
    amount               DECIMAL(18, 2) NOT NULL,
    currency             VARCHAR(3) DEFAULT 'USD',
    is_flagged_high_val  BOOLEAN DEFAULT FALSE,
    ingestion_timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);