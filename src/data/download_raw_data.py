import requests
import pandas as pd
import os
import json

def download_worldbank_data(query, format='json', fct='country_exact,lang_exact', rows="286999", os="0", strdate="2017-01-01", enddate="2025-05-16"):
    url = "https://search.worldbank.org/api/v3/wds?"
    params = {"qterm": query,  "format": format, "fct":fct, "rows": rows, "os": os, "strdate":strdate, "enddate": enddate }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        try:
            return response.json()  # Returns JSON data
        except requests.exceptions.JSONDecodeError:
            print("Response content:", response.text)  # Debugging output
            raise Exception("Failed to parse JSON response")
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, Response: {response.text}")
    
def save_raw_data_to_json(data, filename="data/raw/worldbank_documents.json"):
    print(data)
    # Save data in json file
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)

def save_raw_data_to_csv(data, filename="data/raw/worldbank_documents.csv"):   
    # Extract the documents from the API response
    documents = [
        {
            "id": doc_id,
            "title": doc_data.get("display_title", ""),
            "abstract": doc_data.get("abstracts", {}).get("cdata!", ""),
            "country": doc_data.get("count", ""),
            "date": doc_data.get("docdt", ""),
            "pdf_url": doc_data.get("pdfurl", ""),
            "url": doc_data.get("url", "")
        }
        for doc_id, doc_data in data['documents'].items() if doc_id != "facets" and type(doc_data) == dict # Exclude non-document keys like "facets"
    ]

    # Convert the list of documents to a pandas DataFrame
    df = pd.DataFrame(documents)
    
    # Save the DataFrame to a CSV file
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists
    df.to_csv(filename, index=False)
    print(f"Data has been saved to {filename}")        

if __name__ == "__main__":
    query = ""  # Example query term
    raw_data = download_worldbank_data(query)
    save_raw_data_to_json(raw_data)
    save_raw_data_to_csv(raw_data)
