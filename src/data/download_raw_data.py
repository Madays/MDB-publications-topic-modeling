import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ChunkedEncodingError
from urllib3.util.retry import Retry
import pandas as pd
import os
import json
import time

API_URL = "https://search.worldbank.org/api/v3/wds?"

CORE_FIELDS = [
    "id", "query", "display_title", "abstract", "language", "country", "region",
    "doc_type", "disclosure_date", "keywords", "theme", "subtopic",
    "historic_topics", "pdf_url"
]

session = requests.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[502, 503, 504, 429])
session.mount('https://', HTTPAdapter(max_retries=retries))

def download_worldbank_data(query, format='json', rows_per_page=500, lang_exact='English',
                             fl='display_title,abstracts,lang,count,admreg,docty,disclosure_date,'
                                'keywd,theme,subtopic,historic_topic,pdfurl',
                             strdate="2017-01-01", enddate="2025-05-16", max_records=10000):
    all_docs = {}
    offset = 0
    previous_offset = -1 # To catch accidental reset

    while offset < max_records:
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

        for attempt in range(3):
            try:
                response = session.get(API_URL, params=params, timeout=60)
                break
            except ChunkedEncodingError as e:
                print(f"ChunkedEncodingError: {e}. Retrying ({attempt+1}/3)...")
                time.sleep(2)
        else:
            raise Exception("Failed after multiple attempts due to ChunkedEncodingError")

        if response.status_code == 200:
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
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

        previous_offset = offset
        offset += rows_per_page
        time.sleep(1)

    return {"documents": all_docs}

def save_raw_data_to_json(data, filename, query):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    entry = {"query": query, "response": {"documents": data}}

    existing_data = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

    existing_data.append(entry)
    with open(filename, "w") as f:
        json.dump(existing_data, f, indent=4)

def flatten_document(doc, query):
    def join_nested(d, key):
        return "; ".join(v.get(key, "") for v in d.values()) if isinstance(d, dict) else ""

    return {
        "id": doc.get("id", ""),
        "query": query,
        "display_title": doc.get("display_title", ""),
        "abstract": doc.get("abstracts", {}).get("cdata!", ""),
        "language": doc.get("lang", ""),
        "country": doc.get("count", ""),
        "region": doc.get("admreg", ""),
        "doc_type": doc.get("docty", ""),
        "disclosure_date": doc.get("disclosure_date", ""),
        "keywords": join_nested(doc.get("keywd", {}), "keywd"),
        "theme": doc.get("theme", ""),
        "subtopic": doc.get("subtopic", ""),
        "historic_topics": doc.get("historic_topic", ""),
        "pdf_url": doc.get("pdfurl", "")
    }

def save_raw_data_to_csv(data, filename, query):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    documents = data.get("documents", {})
    rows = [flatten_document(doc, query) for doc in documents.values()]
    df = pd.DataFrame(rows, columns=CORE_FIELDS)
    df.to_csv(filename, mode='a', index=False, header=not os.path.exists(filename))
