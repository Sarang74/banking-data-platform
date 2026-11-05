# 🏛️ Autonomous Core Banking Data Platform
### DuckDB OLAP • Python Ingestion • Data Quality Assertion Gate • One Big Table (OBT)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![DuckDB](https://img.shields.io/badge/DuckDB-2.0+-FFF000?style=for-the-badge&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Storage](https://img.shields.io/badge/Storage-Columnar_Parquet-005C8A?style=for-the-badge)](#)
[![Architecture](https://img.shields.io/badge/Architecture-Quarantine_Gate_%26_OBT-0A85EA?style=for-the-badge)](#)

---

## 🎯 Executive Overview & Architecture

An enterprise-grade core banking data platform designed for high-integrity financial transaction ingestion, automated data quality assertion gating, and sub-second analytical reporting.

The system handles synthetic core transaction feeds (50,000 records) with injected anomalies (negative ledger balances, missing referential keys, high-value AML thresholds). A dedicated assertion gate isolates non-compliant records into audit quarantine while promoting clean transactions to a persistent DuckDB analytical warehouse.

### 📐 End-to-End Pipeline Lineage

```text
                  [ Core Banking Transaction Stream ]
                                   │
                                   ▼
                [ src/ingestion/generate_banking_data.py ]
                                   │
                                   ▼
             data/landing/raw_banking_feed.parquet (50,000 rows)
                                   │
                                   ▼
                [ src/quality/validate_and_quarantine.py ]
                                   │
            ┌──────────────────────┴──────────────────────┐
            ▼                                             ▼
  [ VALIDATED CLEAN RECORDS ]                   [ QUARANTINE ISOLATION ]
   - Strict positive balances                    - Corrupted balances (< 0)
   - Referential integrity intact                - Missing account keys
            │                                             │
            ▼                                             ▼
  data/raw/clean_ledger.parquet        data/quarantine/corrupted_records.parquet
            │                                 (Audit-ready with failure reasons)
            ▼
        [ src/transformation/load_master_obt.py ]
   - Executes DDL (sql/01_create_master_table.sql)
   - Evaluates AML/Risk flags (amount >= $10,000)
            │
            ▼
  DuckDB Warehouse: warehouse.banking_transactions_master
  (data/warehouse/banking_dw.duckdb & data/processed/banking_master_obt.parquet)
            │
            ▼
        [ src/analytics/run_portfolio_queries.py ]
   - Rolling 7-day transaction liquidity (Window Functions)
   - Segment-level AML high-value exposure audit
   - Regional branch settlement performance
