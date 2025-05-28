import pandas as pd
import os

# Set input/output paths
raw_path = "data/raw/worldbank_documents.csv"
interim_dir = "data/interim"
output_path = os.path.join(interim_dir, "stratified_sample.csv")

# Parameters
n_per_query = 200  # Number of documents per query group (or less if not available)

# Create output directory if needed
os.makedirs(interim_dir, exist_ok=True)

# Load raw dataset
df = pd.read_csv(raw_path)

# Clean and filter
df = df[df["abstract"].str.strip().astype(bool)]  # Remove empty abstracts
df = df[df["language"].str.lower() == "english"]  # Keep only English documents

# Stratified sampling by 'query'
df_stratified = (
    df.groupby("query")
    .apply(lambda g: g.sample(n=min(len(g), n_per_query), random_state=42))
    .reset_index(drop=True)
)

# Save result
df_stratified.to_csv(output_path, index=False)
print(f"Stratified sample saved to: {output_path}")
