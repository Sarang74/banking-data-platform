"""
Module: src/quality/validate_and_quarantine.py
Description: Evaluates banking transactions against financial data quality rules,
             quarantines corrupt rows with audit tags, and promotes clean records.
"""

import os
import pandas as pd

def run_quality_gate(
    input_path: str = "data/landing/raw_banking_feed.parquet",
    clean_output_path: str = "data/raw/clean_ledger.parquet",
    quarantine_output_path: str = "data/quarantine/corrupted_records.parquet",
    max_tolerable_error_pct: float = 5.0
):
    print("=" * 65)
    print(" [DATA QUALITY GATE] Initiating Ingestion Audit & Quarantine Gate")
    print("=" * 65)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found at: {input_path}")

    # 1. Load Landing Records
    df = pd.read_parquet(input_path)
    total_records = len(df)
    print(f"[*] Ingested records from landing: {total_records:,}")

    # 2. Rule Evaluation
    # Rule 1: account_id must be populated
    fail_account_id = df["account_id"].isna() | (df["account_id"].astype(str).str.strip() == "")

    # Rule 2: transaction amount must be positive (> 0)
    fail_amount = df["amount"] <= 0

    # Rule 3: transaction_time must be populated
    fail_time = df["transaction_time"].isna()

    # Tag failure reasons
    quarantine_mask = fail_account_id | fail_amount | fail_time

    # 3. Build Quarantine DataFrame with Audit Tags
    quarantine_df = df[quarantine_mask].copy()
    if not quarantine_df.empty:
        reasons = []
        for idx, row in quarantine_df.iterrows():
            row_reasons = []
            if pd.isna(row["account_id"]) or str(row["account_id"]).strip() == "":
                row_reasons.append("NULL_OR_EMPTY_ACCOUNT_ID")
            if row["amount"] <= 0:
                row_reasons.append("NON_POSITIVE_AMOUNT")
            if pd.isna(row["transaction_time"]):
                row_reasons.append("NULL_TRANSACTION_TIMESTAMP")
            reasons.append("; ".join(row_reasons))
        quarantine_df["quarantine_reason"] = reasons

    # 4. Build Clean Ledger DataFrame
    clean_df = df[~quarantine_mask].copy()

    # 5. Export Partitions
    os.makedirs(os.path.dirname(clean_output_path), exist_ok=True)
    os.makedirs(os.path.dirname(quarantine_output_path), exist_ok=True)

    clean_df.to_parquet(clean_output_path, index=False)
    quarantine_df.to_parquet(quarantine_output_path, index=False)

    clean_count = len(clean_df)
    quarantine_count = len(quarantine_df)
    error_rate = (quarantine_count / total_records) * 100

    # 6. Audit Logging Output
    print("\n--- Gate Metrics ---")
    print(f" [+] Validated Clean Records : {clean_count:,} ({clean_count/total_records:.2%})")
    print(f" [!] Quarantined Records     : {quarantine_count:,} ({error_rate:.2f}%)")
    print(f" [-] Clean File Written To   : {clean_output_path}")
    print(f" [-] Quarantine File Written : {quarantine_output_path}")
    print("-" * 65)

    # Circuit breaker check
    if error_rate > max_tolerable_error_pct:
        raise ValueError(
            f"[ALERT] Pipeline Aborted: Quarantine error rate ({error_rate:.2f}%) "
            f"exceeds tolerance threshold ({max_tolerable_error_pct}%)."
        )
    else:
        print("[SUCCESS] Data quality gate passed within operational tolerance!\n")

if __name__ == "__main__":
    run_quality_gate()