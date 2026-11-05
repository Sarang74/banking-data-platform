"""
Module: src/ingestion/generate_banking_data.py
Description: Generates realistic synthetic core banking transactions,
             accounts, and customer datasets with edge cases for quality gating.
"""

import os
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd

fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_banking_batch(num_records: int = 50000, output_dir: str = "data/landing"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Generating {num_records} synthetic core banking records...")

    # 1. Base Customer Pools
    customer_ids = [f"CUST_{1000 + i}" for i in range(200)]
    customer_pool = {
        cid: {
            "customer_name": fake.name(),
            "customer_segment": random.choice(["Retail", "Premium", "Corporate"]),
            "branch_code": random.choice(["BR_LON_01", "BR_MAN_02", "BR_EDI_03", "BR_BIR_04"])
        }
        for cid in customer_ids
    }

    account_types = ["Checking", "Savings", "Credit"]
    categories = ["Payroll", "Wire Transfer", "Retail Purchase", "Utility Bill", "ATM Withdrawal"]

    records = []
    base_date = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        cid = random.choice(customer_ids)
        cust_info = customer_pool[cid]
        tx_time = base_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        
        tx_type = random.choice(["CREDIT", "DEBIT", "TRANSFER"])
        
        # Determine amount & simulate edge cases for Data Quality quarantine
        # 1% chance of invalid negative amount (simulating legacy data corruption)
        if random.random() < 0.01:
            amount = -round(random.uniform(10.0, 500.0), 2)
        # 3% chance of high-value threshold breach (>= 10,000)
        elif random.random() < 0.03:
            amount = round(random.uniform(10000.0, 50000.0), 2)
        else:
            amount = round(random.uniform(5.0, 3500.0), 2)

        # 0.5% chance of missing account_id (referential integrity failure)
        acc_id = None if random.random() < 0.005 else f"ACC_{cid.split('_')[1]}_{random.randint(1, 3)}"

        record = {
            "transaction_id": str(uuid.uuid4()),
            "customer_id": cid,
            "customer_name": cust_info["customer_name"],
            "customer_segment": cust_info["customer_segment"],
            "account_id": acc_id,
            "account_type": random.choice(account_types),
            "branch_code": cust_info["branch_code"],
            "transaction_time": tx_time.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_date": tx_time.strftime("%Y-%m-%d"),
            "transaction_type": tx_type,
            "category": random.choice(categories),
            "amount": amount,
            "currency": "USD"
        }
        records.append(record)

    df = pd.DataFrame(records)

    csv_path = os.path.join(output_dir, "raw_banking_feed.csv")
    parquet_path = os.path.join(output_dir, "raw_banking_feed.parquet")

    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)

    print(f"[+] Successfully wrote {len(df)} records to:")
    print(f"    - CSV:     {csv_path}")
    print(f"    - Parquet: {parquet_path}")

if __name__ == "__main__":
    generate_banking_batch()