"""
Module: src/analytics/run_portfolio_queries.py
Description: Executes core portfolio analytics queries against the DuckDB
             banking warehouse and displays operational KPIs.
"""

import duckdb

def run_analytics(db_path: str = "data/warehouse/banking_dw.duckdb"):
    con = duckdb.connect(db_path)

    print("=" * 80)
    print("QUERY 1: Daily Transaction Volume & 7-Day Moving Total")
    print("=" * 80)
    q1 = """
        WITH daily_rollup AS (
            SELECT 
                transaction_date,
                COUNT(*) AS daily_tx_count,
                ROUND(SUM(amount), 2) AS daily_volume_usd
            FROM warehouse.banking_transactions_master
            GROUP BY transaction_date
        )
        SELECT 
            transaction_date,
            daily_tx_count,
            daily_volume_usd,
            ROUND(SUM(daily_volume_usd) OVER (
                ORDER BY transaction_date 
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            ), 2) AS rolling_7d_volume_usd
        FROM daily_rollup
        ORDER BY transaction_date DESC
        LIMIT 7;
    """
    con.sql(q1).show()

    print("\n" + "=" * 80)
    print("QUERY 2: High-Value Exposure Analysis by Customer Segment (AML Audit)")
    print("=" * 80)
    q2 = """
        SELECT 
            customer_segment,
            COUNT(*) FILTER (WHERE is_flagged_high_val = TRUE) AS high_val_transactions,
            ROUND(SUM(amount) FILTER (WHERE is_flagged_high_val = TRUE), 2) AS high_val_volume_usd,
            ROUND(
                COUNT(*) FILTER (WHERE is_flagged_high_val = TRUE) * 100.0 / COUNT(*), 
                2
            ) AS pct_of_segment_tx
        FROM warehouse.banking_transactions_master
        GROUP BY customer_segment
        ORDER BY high_val_volume_usd DESC;
    """
    con.sql(q2).show()

    print("\n" + "=" * 80)
    print("QUERY 3: Top Branch Performance by Transaction Liquidity")
    print("=" * 80)
    q3 = """
        SELECT 
            branch_code,
            COUNT(*) AS total_transactions,
            ROUND(SUM(amount), 2) AS total_settled_usd,
            ROUND(AVG(amount), 2) AS avg_ticket_size_usd
        FROM warehouse.banking_transactions_master
        GROUP BY branch_code
        ORDER BY total_settled_usd DESC;
    """
    con.sql(q3).show()

    con.close()
    print("[SUCCESS] All portfolio analytics queries executed successfully!\n")

if __name__ == "__main__":
    run_analytics()