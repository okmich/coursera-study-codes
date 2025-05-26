from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from pymongo import MongoClient
from typing import Optional

from getpass import getpass
from urllib.parse import quote_plus

import os
import requests
import zipfile
import pandas as pd

def get_mongodb_client():
    password = quote_plus(getpass("Enter your MongoDB password: "))
    uri = f"mongodb+srv://db-user-1:{password}@vectordb-cluster.w7wuq3x.mongodb.net/?retryWrites=true&w=majority&appName=vectordb-cluster"
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


def get_online_retail_dataset():
    os.makedirs('data', exist_ok=True)
    
    dataset_url = 'https://archive.ics.uci.edu/static/public/352/online+retail.zip'
    zip_path = os.path.join(os.path.dirname(os.getcwd()), 'online_retail.zip')
    data_file_path = os.path.join(os.path.dirname(os.getcwd()), 'data', 'Online Retail.xlsx')
    
    # Check if the xlsx file already exists
    if not os.path.exists(data_file_path):
        try:
            # Download the dataset
            print("Downloading dataset...")
            response = requests.get(dataset_url)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Save the zip file
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.dirname(data_file_path))
            
            print("Dataset downloaded and extracted successfully.")
            
            # Remove the zip file after extraction
            os.remove(zip_path)
        except Exception as e:
            print(f"Error downloading or extracting dataset: {e}")
            return None
    
    # Read the data file and return records as a list of dictionaries
    try:
        df = pd.read_excel(data_file_path)
        records = df.to_dict('records')
        return records
    except Exception as e:
        print(f"Error reading xlsx file: {e}")
        return None


def load_sales_data_to_mongodb() -> Optional[int]:
    client = get_mongodb_client()
    if not client:
        print("Failed to connect to MongoDB")
        return None
    
    records = get_online_retail_dataset()
    if not records:
        print("Failed to retrieve dataset")
        return None
    
    collection_name = "invoice"
    try:
        db = client["online_retail_db"]  # Database name
        collection = db[collection_name]
        
        batch_size = 1000
        inserted_count = 0
        
        # clear collection
        collection.delete_many({})
        
        for i in range(0, 10000, batch_size):
            batch = records[i:i + batch_size]
            result = collection.insert_many(batch)
            inserted_count += len(result.inserted_ids)
            print(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} records")
        
        print(f"Successfully inserted {inserted_count} documents into '{collection_name}' collection")
        return inserted_count
        
    except Exception as e:
        print(f"Error loading data to MongoDB: {e}")
        return None
    finally:
        client.close()


if __name__ == "__main__":
    if load_sales_data_to_mongodb():
        print("Data loaded successfully")
    else:
        print("Failed to load data")
