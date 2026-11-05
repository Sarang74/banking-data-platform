-- =====================================================================
-- Banking Platform Analytics & Audit Queries
-- Engine: DuckDB / ANSI SQL
-- =====================================================================

-- 1. Daily Settlement Reconciliation (Total Debits vs Credits by Date)
SELECT 
    transaction_date,
    COUNT(transaction_id) AS total_transactions,
    SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE 0 END) AS total_credit_volume,
    SUM(CASE WHEN transaction_type = 'DEBIT' THEN amount ELSE 0 END) AS total_debit_volume,
    ROUND(
        SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE -amount END), 2
    ) AS net_settlement_balance
FROM warehouse.banking_transactions_master
GROUP BY transaction_date
ORDER BY transaction_date DESC;

-- 2. Customer Running Account Balances using Window Functions
SELECT 
    transaction_id,
    customer_id,
    account_id,
    transaction_time,
    transaction_type,
    amount,
    SUM(CASE WHEN transaction_type = 'CREDIT' THEN amount ELSE -amount END) 
        OVER (
            PARTITION BY account_id 
            ORDER BY transaction_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_account_balance
FROM warehouse.banking_transactions_master
ORDER BY account_id, transaction_time;

-- 3. High-Value Transfer Audit (CTEs + Anomaly Filtering)
WITH high_value_transfers AS (
    SELECT 
        transaction_id,
        customer_id,
        customer_name,
        branch_code,
        category,
        amount,
        transaction_time
    FROM warehouse.banking_transactions_master
    WHERE amount >= 10000.00
)
SELECT 
    branch_code,
    COUNT(transaction_id) AS high_val_count,
    ROUND(SUM(amount), 2) AS total_flagged_exposure
FROM high_value_transfers
GROUP BY branch_code
ORDER BY total_flagged_exposure DESC;