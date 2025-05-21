import requests
import pandas as pd
import os
import json
from taxonomy import ALL_TAXONOMY_TERMS
  
def download_worldbank_data(query, format='json', fl="abstracts,docdt,count", rows='558893', strdate="2017-01-01", enddate="2025-05-16"):
    url = "https://search.worldbank.org/api/v3/wds?"
    params = {"qterm": query,  "format": format, "rows": rows, "strdate":strdate, "enddate": enddate }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        try:
            return response.json()  # Returns JSON data
        except requests.exceptions.JSONDecodeError:
            print("Response content:", response.text)  # Debugging output
 
            raise Exception("Failed to parse JSON response")
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, Response: {response.text}")
    
def save_raw_data_to_json(data, filename, query):
    """
    Save the response data for a given query into a JSON file.
    The file will contain a list of objects, each with 'query' and 'response' keys.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    entry = {"query": query, "response": data}
    # Load existing data if file exists
    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            try:
                existing_data = json.load(json_file)
                if not isinstance(existing_data, list):
                    existing_data = []
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    existing_data.append(entry)
    with open(filename, "w") as json_file:
        json.dump(existing_data, json_file, indent=4)

def flatten_document(doc):
    """Flatten nested fields in a document dictionary for CSV output."""
    flat = {}
    for key, value in doc.items():
        if isinstance(value, dict):
            # Join all nested values as a string, separated by '; '
            flat[key] = '; '.join(str(v).lower() for v in value.values())
        elif isinstance(value, list):
            flat[key] = '; '.join(str(v).lower() for v in value)
        else:
            flat[key] = value
    print('flat', flat)
    return flat

def save_raw_data_to_csv(data, filename, query=None):
    """
    Save the 'documents' part of the response data into a CSV file.
    Each document will be a row. Nested fields are flattened.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    documents = data.get("documents", {})
    if not documents:
        print("No documents found in data.")
        return

    # Flatten all documents and collect headers
    rows = []
    for doc_id, doc in documents.items():
        flat_doc = flatten_document(doc)
        flat_doc["query"] = query  # Optionally add the query term as a column
        rows.append(flat_doc)

    # Get all possible headers
    headers = set()
    for row in rows:
        headers.update(row.keys())
    headers = sorted(headers)

    # Write to CSV (append if file exists, else write header)
    write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
    df = pd.DataFrame(rows, columns=headers)
    df.to_csv(filename, mode='a', header=write_header, index=False)
    
if __name__ == "__main__":
    # Ensure the JSON file is empty on first run
    json_path = "data/raw/worldbank_documents.json"
    csv_path = "data/raw/worldbank_documents.csv"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        f.write("[]")  # Write empty list to start
    # Remove the CSV file if it exists to start from scratch
    if os.path.exists(csv_path):
        os.remove(csv_path)
    query = "artificial intelligence"  # Example query term
    for query in ALL_TAXONOMY_TERMS:
        raw_data = download_worldbank_data(query)
        #save_raw_data_to_json(raw_data, json_path, query)
        save_raw_data_to_csv(raw_data, csv_path, query)
