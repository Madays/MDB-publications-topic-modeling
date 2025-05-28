import pandas as pd
import os

raw_path = "data/raw/worldbank_documents.csv"
interim_path = "data/interim/shuffled_documents.csv"

# Ensure output directory exists
os.makedirs(os.path.dirname(interim_path), exist_ok=True)

# Specify the columns you want to keep and their order
columns = [
    "id", "display_title", "abstract", "language",
    "keywords", "topics", "historic_topics", "query"
]

# Load the raw data
df = pd.read_csv(raw_path, usecols=columns)

# Drop rows with empty abstracts
df = df[df["abstract"].str.strip().astype(bool)]

# Shuffle the DataFrame
df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save the shuffled data
df_shuffled.to_csv(interim_path, index=False)
print(f"Saved shuffled dataset to {interim_path}")
