from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from getpass import getpass
from urllib.parse import quote_plus

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


if __name__ == "__main__":
    client = get_mongodb_client()
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


