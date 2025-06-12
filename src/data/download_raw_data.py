"""
This script downloads and saves raw data from the World Bank API based on a list of taxonomy search terms.

Modules:
    - requests: For making HTTP requests to the World Bank API.
    - pandas: For handling and saving tabular data.
    - os: For file and directory operations.
    - json: For reading and writing JSON files.
    - taxonomy: Imports ALL_TAXONOMY_TERMS, a list of search terms.

Constants:
    - API_URL: Base URL for the World Bank API.
    - CORE_FIELDS: List of fields to extract and save from each document.

Functions:
    - download_worldbank_data(query, format='json', rows='558893', lang_exact='English', fl=..., strdate="2017-01-01", enddate="2025-05-16"):
        Downloads data from the World Bank API for a given query and returns the JSON response.
        Raises an exception if the request fails or the response cannot be parsed as JSON.

    - save_raw_data_to_json(data, filename, query):
        Saves the raw API response to a JSON file, appending each new query and its response as an entry in a list.

    - flatten_document(doc, query):
        Flattens a single document from the API response into a dictionary with selected fields for easier tabular storage.

    - save_raw_data_to_csv(data, filename, query=None):
        Converts the API response into a flat tabular format and appends it to a CSV file.

Main Execution:
    - Initializes empty JSON and CSV files for storing results.
    - Iterates over all taxonomy terms, downloads data for each, and saves both the raw JSON and flattened CSV data.

Usage:
    Run this script directly to download and save World Bank documents for all taxonomy terms defined in taxonomy.ALL_TAXONOMY_TERMS.

Note:
    - The script expects the taxonomy module with ALL_TAXONOMY_TERMS to be available.
    - Output files are saved in the 'data/raw/' directory.
"""
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ChunkedEncodingError
from urllib3.util.retry import Retry
import pandas as pd
import os
import json
import time  # optional, to avoid hitting the API too fast
# List of search terms
from topics import ALL_TAXONOMY_TERMS

# Set up requests session with retry strategy
session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[502, 503, 504, 429])
session.mount('https://', HTTPAdapter(max_retries=retries))

total_terms = len(ALL_TAXONOMY_TERMS)
#https://search.worldbank.org/api/v3/wds?format=json&qterm=agriculture,%20fishing%20and%20forestry&lang_exact=English&fl=abstracts,display_title,keywd,subtopic,teratopic,historic_topic&rows=558893
# example of facets https://search.worldbank.org/api/v3/wds?format=json&fct=sectr_exact,count_exact,lang_exact&rows=10&count_exact=Russian%20Federation%5eArmenia&lang_exact=Russian%5eFrench
API_URL = "https://search.worldbank.org/api/v3/wds?"

"""CORE_FIELDS = [
    "id", "display_title", "abstract", "language", "country", "region",
    "doc_type", "major_doc_type", "doc_date", "disclosure_date",
    "keywords", "authors", "sectors", "subsector", "themes",
    "topics", "historic_topics", "pdf_url", "txt_url", "url", "query"
]"""
CORE_FIELDS = [
    "id", "query", "display_title", "abstract", "language", "country", "region", "doc_type","disclosure_date", "keywords","theme", "subtopic", "historic_topics", "pdf_url"
]

def download_worldbank_data(
        query, 
        format='json', 
        rows_per_page=500, 
        lang_exact='English', 
        fl='display_title,abstracts,lang,count,admreg,docty,disclosure_date,keywd,theme,subtopic,historic_topic,pdfurl',
        strdate="2017-01-01", 
        enddate="2025-05-16",
        max_records=10000
    ):

    all_docs = {}
    offset= 0
    previous_offset = -1  # To catch accidental reset
    
    while offset < max_records:
        #what slice of results you're asking for
        print(f"Requesting offset {offset}...")

        if offset == previous_offset:
            print("Offset repeated — stopping to prevent infinite loop.")
            break

        params = {
            "qterm": query,
            "format": format,
            "lang_exact": lang_exact,
            "rows": rows_per_page,
            "os": offset,        
            "fl": fl,
            "strdate": strdate,
            "enddate": enddate
        }

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = session.get(API_URL, params=params, timeout=60)
                break  # Success!
            except ChunkedEncodingError as e:
                print(f"ChunkedEncodingError: {e}. Retrying ({attempt+1}/{max_attempts})...")
                time.sleep(2)
        else:
            raise Exception("Failed after multiple attempts due to ChunkedEncodingError")
        
        if response.status_code == 200:
            try:
                #Store the parsed JSON
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                print("Response content:", response.text)
                raise Exception("Failed to parse JSON response")
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}, Response: {response.text}")
        
        #dictionary comprehension: Pulls all key–value pairs from the "documents" object in the API response and excludes the "facets" entry, which is not a document, but just metadata
        docs = {k: v for k, v in data.get("documents", {}).items() if k != "facets"}
        if not docs:
            print("No more documents found.")
            break
        
        previous_count = len(all_docs)
        #adds all the documents from the current batch into the larger dictionary
        all_docs.update(docs)

        # 💡 Detect infinite loop
        if len(all_docs) == previous_count:
            print("No new documents added — stopping to prevent infinite loop.")
            break

        # ✅ Calculate progress for each term
        progress = (len(all_docs) / max_records) * 100
        print(f"Downloaded {len(all_docs)} documents... ({progress:.2f}%)")

        #Track previous_offset to catch re-loops
        previous_offset = offset
        # Move to next batch
        offset += rows_per_page

        # Pause between requests (good API etiquette)
        time.sleep(1)  
    return {"documents": all_docs}
    

def save_raw_data_to_json(data, filename, query):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # Filter data to include only documents with 'abstracts' property
    if "documents" in data and isinstance(data["documents"], dict):
        filtered_docs = {
            k: v for k, v in data["documents"].items()
            if "abstracts" in v and len(v["abstracts"].get("cdata!", "")) > 300
        }
        data = {**data, "documents": filtered_docs}
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
        "query": query,
        "display_title": doc.get("display_title", ""),
        "abstract": doc.get("abstracts", {}).get("cdata!", ""),
        "language": doc.get("lang", ""),
        "country": doc.get("count", ""),
        "region": doc.get("admreg", ""),
        "doc_type": doc.get("docty", ""),
        #"major_doc_type": doc.get("majdocty", ""),
        #"doc_date": doc.get("docdt", ""),
        "disclosure_date": doc.get("disclosure_date", ""),
        "keywords": join_nested(doc.get("keywd", {}), "keywd"),
        #"authors": join_nested(doc.get("authors", {}), "author"),
        #"sectors": join_nested(doc.get("sectr_exact", {}), "sectr_exact"),
        #"subsector": doc.get("subsc", ""),
        "theme": doc.get("theme", ""),
        "subtopic": doc.get("subtopic", ""),
        "historic_topics": doc.get("historic_topic", ""),
        "pdf_url": doc.get("pdfurl", ""),
        #"txt_url": doc.get("txturl", ""),
        #"url": doc.get("url", ""),
        
    }
    return flat

def save_raw_data_to_csv(data, filename, query=None):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    documents = data.get("documents", {})
    if not documents:
        print("No documents found in data.")
        return

    rows = [
        flatten_document(doc, query)
        for doc in documents.values()
        if 'abstracts' in doc and len(doc['abstracts'].get('cdata!', "")) > 300
    ]
    df = pd.DataFrame(rows, columns=CORE_FIELDS)
    write_header = not os.path.exists(filename)
    df.to_csv(filename, mode="a", header=write_header, index=False)

if __name__ == "__main__":
    json_path = "data/raw/worldbank_documents.js"
    csv_path = "data/raw/worldbank_documents.csv"
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        f.write("[]")
    if os.path.exists(csv_path):
        os.remove(csv_path)
    for i, term in enumerate(ALL_TAXONOMY_TERMS, 1):
        #Track total progress 
        print(f"\n[{i}/{total_terms}] Fetching data for: {term}")
        raw_data = download_worldbank_data(query=term)
        save_raw_data_to_json(raw_data, json_path, query=term)
        save_raw_data_to_csv(raw_data, csv_path, query=term)

