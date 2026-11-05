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

\\\	ext
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
   - Evaluates AML/Risk flags (amount >= \,000)
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
\\\

---

## 📂 Repository Structure

\\\	ext
banking-data-platform/
│
├── data/
│   ├── landing/                  # Raw simulated incoming transaction feeds
│   ├── raw/                      # Validated clean ledger records
│   ├── quarantine/               # Isolated corrupted records with failure tags
│   ├── warehouse/                # Persistent DuckDB warehouse (banking_dw.duckdb)
│   └── processed/                # Materialized OBT Parquet extracts
│
├── sql/
│   ├── 01_create_master_table.sql# DDL schema definition for master OBT
│   └── 02_analytics_queries.sql  # Portfolio SQL analytical queries
│
├── src/
│   ├── ingestion/
│   │   └── generate_banking_data.py   # Synthetic transaction generator
│   ├── quality/
│   │   └── validate_and_quarantine.py # Financial validation & quarantine engine
│   ├── transformation/
│   │   └── load_master_obt.py         # DuckDB DDL execution & OBT loader
│   └── analytics/
│       └── run_portfolio_queries.py   # Analytical KPI reporting suite
│
├── inspect_data.py               # Standalone SQL inspection scratchpad
├── requirements.txt              # Pinned project dependencies
└── README.md                     # Technical architecture documentation
\\\

---

## 🛡️ Data Quality Gate & Circuit-Breaker Rules

Financial institutions require that corrupt data never silently enters warehouse models:
- **Referential Integrity:** ccount_id must be non-null and non-empty.
- **Financial Sanity:** Transaction mount must be strictly positive (> 0).
- **Temporal Consistency:** Timestamp must be valid and populated.
- **Automated Quarantine:** Failing records are tagged with an explicit quarantine_reason and stored in data/quarantine/corrupted_records.parquet.
- **Operational Circuit Breaker:** If the quarantine error rate exceeds **5.0%**, the ingestion pipeline aborts immediately to protect downstream systems.

---

## 📊 Analytical Capabilities

The analytical suite leverages DuckDB's vectorized engine to execute complex financial SQL:
1. **Window Aggregations:** Computes rolling 7-day cumulative settlement volumes (SUM(amount) OVER (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)).
2. **AML & High-Value Auditing:** Classifies transactions $\ge \,000.00$ with is_flagged_high_val = TRUE and aggregates concentration risk by customer segment (Corporate, Premium, Retail).
3. **Branch Performance:** Evaluates settlement density and average ticket size across regional branch networks.

---

## 🚀 Quickstart & Local Reproduction

\\\powershell
# 1. Clone repository and set up environment
git clone https://github.com/Sarang74/banking-data-platform.git
cd banking-data-platform
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# 2. Ingest synthetic banking feed (50k records)
python src\ingestion\generate_banking_data.py

# 3. Execute quality assertion gate & quarantine isolation
python src\quality\validate_and_quarantine.py

# 4. Load master OBT into DuckDB warehouse
python src\transformation\load_master_obt.py

# 5. Run analytical queries
python src\analytics\run_portfolio_queries.py
\\\

---

## 📄 License
MIT License