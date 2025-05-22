import requests
import pandas as pd
import os
import json

# List of search terms
from taxonomy import ALL_TAXONOMY_TERMS

API_URL = "https://search.worldbank.org/api/v3/wds"

CORE_FIELDS = [
    "id", "display_title", "abstract", "language", "country", "region",
    "doc_type", "major_doc_type", "doc_date", "disclosure_date",
    "keywords", "authors", "sectors", "subsector", "themes",
    "topics", "historic_topics", "pdf_url", "txt_url", "url", "query"
]

def download_worldbank_data(query, format='json', rows='558893', strdate="2017-01-01", enddate="2025-05-16"):
    params = {
        "qterm": query,
        "format": format,
        "rows": rows,
        "strdate": strdate,
        "enddate": enddate
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print("Response content:", response.text)
            raise Exception("Failed to parse JSON response")
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, Response: {response.text}")

def save_raw_data_to_json(data, filename, query):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    entry = {"query": query, "response": data}
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

def flatten_document(doc, query):
    def join_nested(d, key):
        return "; ".join(v.get(key, "") for v in d.values()) if isinstance(d, dict) else ""

    flat = {
        "id": doc.get("id", ""),
        "display_title": doc.get("display_title", ""),
        "abstract": doc.get("abstracts", {}).get("cdata!", ""),
        "language": doc.get("lang", ""),
        "country": doc.get("count", ""),
        "region": doc.get("admreg", ""),
        "doc_type": doc.get("docty", ""),
        "major_doc_type": doc.get("majdocty", ""),
        "doc_date": doc.get("docdt", ""),
        "disclosure_date": doc.get("disclosure_date", ""),
        "keywords": join_nested(doc.get("keywd", {}), "keywd"),
        "authors": join_nested(doc.get("authors", {}), "author"),
        "sectors": join_nested(doc.get("sectr", {}), "sector"),
        "subsector": doc.get("subsc", ""),
        "themes": doc.get("theme", ""),
        "topics": doc.get("subtopic", ""),
        "historic_topics": doc.get("historic_topic", ""),
        "pdf_url": doc.get("pdfurl", ""),
        "txt_url": doc.get("txturl", ""),
        "url": doc.get("url", ""),
        "query": query
    }
    return flat

def save_raw_data_to_csv(data, filename, query=None):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    documents = data.get("documents", {})
    if not documents:
        print("No documents found in data.")
        return

    rows = [flatten_document(doc, query) for doc in documents.values()]
    df = pd.DataFrame(rows, columns=CORE_FIELDS)
    write_header = not os.path.exists(filename)
    df.to_csv(filename, mode="a", header=write_header, index=False)

if __name__ == "__main__":
    json_path = "data/raw/worldbank_documents.json"
    csv_path = "data/raw/worldbank_documents.csv"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        f.write("[]")
    if os.path.exists(csv_path):
        os.remove(csv_path)
    for query in ALL_TAXONOMY_TERMS:
        raw_data = download_worldbank_data(query)
        save_raw_data_to_json(raw_data, json_path, query)
        save_raw_data_to_csv(raw_data, csv_path, query)