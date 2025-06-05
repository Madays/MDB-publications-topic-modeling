import pandas as pd
import os

# Set input/output paths
raw_path = "data/raw/worldbank_documents.csv"
interim_dir = "data/interim"
output_path = os.path.join(interim_dir, "stratified_sample.csv")

# Create output directory if needed
os.makedirs(interim_dir, exist_ok=True)

# Load raw dataset
df = pd.read_csv(raw_path)
# Count number of documents for each query
documents_for_query = df["query"].value_counts()
# Remove outlier queries (e.g., those with extremely low counts)
q_low = documents_for_query.quantile(0.01)
valid_documents = documents_for_query[(documents_for_query >= q_low)].index
df = df[df["query"].isin(valid_documents)]

# Clean and filter
df = df[df["abstract"].str.strip().astype(bool)]  # Remove empty abstracts
df = df[df["language"].str.lower() == "english"]  # Keep only English documents

# Parameters
# Count number of documents for each query
documents_for_query = df["query"].value_counts()
n_per_query = documents_for_query.min()  # Number of documents per query group (or less if not available)
print(n_per_query)
# Stratified sampling by 'query'
df_stratified = (
    df.groupby("query")
    .apply(lambda g: g.sample(n=min(len(g), n_per_query), random_state=42))
    .reset_index(drop=True)
)

# Save result
df_stratified.to_csv(output_path, index=False)
print(f"Stratified sample saved to: {output_path}")
