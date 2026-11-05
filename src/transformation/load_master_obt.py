"""
Module: src/transformation/load_master_obt.py
Description: Loads validated clean banking records into the DuckDB warehouse,
             executes DDL, applies business flags, and materializes the master OBT.
"""

import os
import duckdb

def transform_and_load_master(
    clean_input_path: str = "data/raw/clean_ledger.parquet",
    db_path: str = "data/warehouse/banking_dw.duckdb",
    processed_parquet_path: str = "data/processed/banking_master_obt.parquet"
):
    print("=" * 70)
    print(" [TRANSFORMATION & LOAD] Promoting Clean Ledger to Master OBT Warehouse")
    print("=" * 70)

    if not os.path.exists(clean_input_path):
        raise FileNotFoundError(f"Clean ledger not found at: {clean_input_path}")

    # Ensure output directories exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(os.path.dirname(processed_parquet_path), exist_ok=True)

    # 1. Connect to persistent DuckDB database
    con = duckdb.connect(db_path)
    print(f"[*] Connected to DuckDB warehouse: {db_path}")

    # 2. Execute DDL from sql/01_create_master_table.sql
    ddl_path = "sql/01_create_master_table.sql"
    if os.path.exists(ddl_path):
        with open(ddl_path, "r") as f:
            ddl_sql = f.read()
        con.execute(ddl_sql)
        print(" [+] Executed master schema DDL (warehouse.banking_transactions_master)")
    else:
        raise FileNotFoundError(f"DDL script not found at {ddl_path}")

    # 3. Insert and transform clean records into the OBT
    # Enforces business flag: is_flagged_high_val = TRUE if amount >= 10,000
    insert_sql = f"""
        INSERT OR REPLACE INTO warehouse.banking_transactions_master
        SELECT 
            transaction_id,
            customer_id,
            customer_name,
            customer_segment,
            account_id,
            account_type,
            branch_code,
            CAST(transaction_time AS TIMESTAMP) AS transaction_time,
            CAST(transaction_date AS DATE) AS transaction_date,
            transaction_type,
            category,
            CAST(amount AS DECIMAL(18, 2)) AS amount,
            currency,
            CASE WHEN amount >= 10000.00 THEN TRUE ELSE FALSE END AS is_flagged_high_val,
            CURRENT_TIMESTAMP AS ingestion_timestamp
        FROM '{clean_input_path}';
    """
    con.execute(insert_sql)

    # 4. Verify record count in warehouse
    count_res = con.execute("SELECT COUNT(*) FROM warehouse.banking_transactions_master;").fetchone()[0]
    high_val_count = con.execute(
        "SELECT COUNT(*) FROM warehouse.banking_transactions_master WHERE is_flagged_high_val = TRUE;"
    ).fetchone()[0]

    print(f" [+] Total Master OBT Records Loaded : {count_res:,}")
    print(f" [+] High-Value Transactions Flagged : {high_val_count:,}")

    # 5. Export materialized OBT to columnar Parquet for downstream fast scans
    export_sql = f"""
        COPY warehouse.banking_transactions_master 
        TO '{processed_parquet_path}' (FORMAT PARQUET);
    """
    con.execute(export_sql)
    print(f" [+] Exported Master OBT Parquet     : {processed_parquet_path}")

    con.close()
    print("[SUCCESS] Master OBT transformation and load completed successfully!\n")

if __name__ == "__main__":
    transform_and_load_master()