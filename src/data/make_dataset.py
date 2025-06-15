import os
from download_raw_data import download_worldbank_data, save_raw_data_to_json, save_raw_data_to_csv
from querys import ALL_TAXONOMY_TERMS

def make_dataset(json_path="data/raw/worldbank_documents.js",
                 csv_path="data/raw/worldbank_documents.csv",
                 max_records=10000):
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        f.write("[]")

    if os.path.exists(csv_path):
        os.remove(csv_path)

    for i, term in enumerate(ALL_TAXONOMY_TERMS, 1):
        print(f"\n[{i}/{len(ALL_TAXONOMY_TERMS)}] Fetching data for: {term}")
        data = download_worldbank_data(query=term, max_records=max_records)
        save_raw_data_to_json(data, json_path, query=term)
        save_raw_data_to_csv(data, csv_path, query=term)

if __name__ == "__main__":
    make_dataset()