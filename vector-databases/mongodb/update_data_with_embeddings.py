from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo

from getpass import getpass
from urllib.parse import quote_plus

import tensorflow_hub as hub


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

def update_normalized_descriptions(model):
    batch_size = 500
    client = None
    try:
        client = get_mongodb_client()
        if not client:
            print("Failed to connect to MongoDB")
            return None
        
        db = client["online_retail_db"]
        collection = db["invoice"]
        
        updated_count = 0
        last_id = None
        
        while True:
            query = {}
            if last_id:
                query["_id"] = {"$gt": last_id}
            
            cursor = collection.find(query).sort("_id").limit(batch_size)
            batch = list(cursor)
            
            if not batch:
                break 
            
            bulk_operations = []
            for doc in batch:
                try:
                    desc = doc.get("Description", "")
                    if len(desc) > 1:
                        embedding = model([desc])[0].numpy().tolist()  # model -> tensor -> numpy ndarray -> python array
                        bulk_operations.append(
                            pymongo.UpdateOne(
                                {"_id": doc["_id"]},
                                {"$set": {"desc_embeddeing": embedding}}
                            )
                        )
                except Exception as e:
                    print(f"Error transforming : {desc}")
            
            # Execute bulk update
            if bulk_operations:
                result = collection.bulk_write(bulk_operations)
                updated_count += result.modified_count
                print(f"Processed batch - Updated {result.modified_count} documents (Total: {updated_count})")
            
            # Track last ID for next batch
            last_id = batch[-1]["_id"]
        
        print(f"Successfully updated {updated_count} documents with normalized descriptions")
        return updated_count
        
    except Exception as e:
        print(f"Error updating documents: {e}")
        return None
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    model = load_model()
    updated_count = update_normalized_descriptions(model)
    if updated_count is not None:
        print(f"Total documents updated: {updated_count}")

