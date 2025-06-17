import os
import json
from download_raw_data import download_worldbank_data, save_raw_data_to_json, save_raw_data_to_csv
from querys import ALL_TAXONOMY_TERMS

def make_dataset(json_path="data/raw/worldbank_documents.json",
                 csv_path="data/raw/worldbank_documents.csv",
                 fetched_query = "src/data/fetched_querys.json",
                 max_records=10000):

    # Load existing queries from the fetched_query file if it exists
    existing_queries = set()
    if os.path.exists(fetched_query):
        with open(fetched_query, "r", encoding="utf-8") as f:
            content = f.read().strip()
            data = {}
            if content:
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    data = {}
            existing_queries = set(data.get('queries', []))

    for query in ALL_TAXONOMY_TERMS:
        if query in existing_queries:
            print(f"Skipping already fetched query: {query}")
            continue
        print(f"Fetching data for: {query}")
        raw_data = download_worldbank_data(query=query, max_records=max_records)
        # Save the fetched query to the fetched_query file
        existing_queries.add(query)
        with open(fetched_query, "w", encoding="utf-8") as f:
            json.dump({'queries': list(existing_queries)}, f, ensure_ascii=False, indent=2)
        save_raw_data_to_json(raw_data, json_path, query)
        save_raw_data_to_csv(raw_data, csv_path, query)

if __name__ == "__main__":
    make_dataset()