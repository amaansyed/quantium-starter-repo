import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

csv_files = [
    "daily_sales_data_0.csv",
    "daily_sales_data_1.csv",
    "daily_sales_data_2.csv",
]

dfs = []

for filename in csv_files:
    file_path = os.path.join(DATA_DIR, filename)
    print(f"Reading {file_path}...")
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    pink_df = df[df["product"] == "pink morsel"]
    
    pink_df["Sales"] = pink_df["price"] * pink_df["quantity"]
    
    formatted = pink_df[["Sales", "date", "region"]].copy()
    
    formatted = formatted.rename(
        columns={
            "date": "Date",
            "region": "Region",
        }
    )
    
    dfs.append(formatted)

combined = pd.concat(dfs, ignore_index=True)

# Output file path
output_path = os.path.join(DATA_DIR, "pink_morsel_sales.csv")

# Save to CSV
combined.to_csv(output_path, index=False)

print(f"Done! Wrote combined data to {output_path}")
