from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo

from getpass import getpass
from urllib.parse import quote_plus

import tensorflow_hub as hub

import sys


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

def get_embedding(text: str) -> str:
    """Normalize text by converting to lowercase, removing special chars, and normalizing unicode"""
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    return text


def load_model():
    # https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    model = hub.load(module_url)
    return model


def vector_search(model, collection, query_text: str, num_candidates: int = 10, limit: int = 5, score_threshold: float = 0.0):
    try:
        query_embedding = model([query_text])[0].numpy().tolist()
        pipeline = [
            {
                '$vectorSearch': {
                    "index": "vector_index",
                    "path": "desc_embedding",
                    'queryVector': query_embedding,
                    'numCandidates': num_candidates,
                    'limit': limit
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'InvoiceNo': 1,
                    'StockCode': 1,
                    'Quantity': 1,
                    'Description': 1,
                    'InvoiceDate': 1,
                    'UnitPrice': 1,
                    'Country': 1,
                    'score': {'$meta': 'vectorSearchScore'}
                }
            },
            {
                '$match': {
                    'score': {'$gt': score_threshold}
                }
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        return results
        
    except Exception as e:
        print(f"Error performing vector search: {e}")
        return []


if __name__ == "__main__":
    model = load_model()
    try:
        client = get_mongodb_client()
        if not client:
            print("Failed to connect to MongoDB")
            sys.exit(-1)
                    
        db = client["online_retail_db"]
        collection = db["invoice"]

        while True:
            user_input = input("Enter your text: ")
            if user_input == 'quit':
                break

            results = vector_search(model, collection, user_input)
            print("\n\nSearch Result:")
            print(results)
                
    except Exception as e:
        print(f"Error updating documents: {e}")
    finally:
        if client:
            client.close()
