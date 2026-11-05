"""
Module: inspect_data.py
Description: Audits and verifies the materialized master OBT in DuckDB warehouse.
"""

import duckdb

db_path = "data/warehouse/banking_dw.duckdb"
con = duckdb.connect(db_path)

print("=" * 80)
print("1. MASTER OBT AUDIT: Overall Record Count & High-Value Flag Summary")
print("=" * 80)
query_flags = """
    SELECT 
        is_flagged_high_val,
        COUNT(*) AS record_count,
        ROUND(MIN(amount), 2) AS min_amount,
        ROUND(MAX(amount), 2) AS max_amount,
        ROUND(AVG(amount), 2) AS avg_amount
    FROM warehouse.banking_transactions_master
    GROUP BY is_flagged_high_val
    ORDER BY is_flagged_high_val DESC;
"""
con.sql(query_flags).show()

print("\n" + "=" * 80)
print("2. DATA SANITY AUDIT: Assert Zero Quarantine Violations in Master Table")
print("=" * 80)
query_sanity = """
    SELECT 
        COUNT(*) FILTER (WHERE amount <= 0) AS invalid_amounts_count,
        COUNT(*) FILTER (WHERE account_id IS NULL) AS missing_account_ids_count
    FROM warehouse.banking_transactions_master;
"""
con.sql(query_sanity).show()

print("\n" + "=" * 80)
print("3. SEGMENT METRICS: Revenue Distribution Across Customer Segments")
print("=" * 80)
query_segments = """
    SELECT 
        customer_segment,
        COUNT(*) AS transaction_count,
        ROUND(SUM(amount), 2) AS total_volume_usd,
        ROUND(AVG(amount), 2) AS avg_ticket_size
    FROM warehouse.banking_transactions_master
    GROUP BY customer_segment
    ORDER BY total_volume_usd DESC;
"""
con.sql(query_segments).show()

con.close()