import psycopg
from psycopg import sql
from urllib.parse import quote_plus
from getpass import getpass

import os

import numpy as np

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow_hub as hub


# PostgreSQL connection configuration
config = {
    "host": "localhost",
    "dbname": "postgres",
    "port": 5432,
    "user": "test_user"
}

# Array of sentences to be inserted into the database
sentences = [
    "The horse is galloping",
    "The owl is hooting",
    "The rabbit is hopping",
    "The koala is munching",
    "The penguin is waddling",
    "The kangaroo is hopping",
    "The fox is prowling",
    "The parrot is squawking",
    "The turtle is crawling",
    "The cheetah is sprinting"
]

def load_model():
    # https://www.tensorflow.org/hub/tutorials/semantic_similarity_with_tf_hub_universal_encoder
    module_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
    model = hub.load(module_url)
    return model

def cosine_similarity(v1, v2):
    a = np.array(v1)
    b = np.array(v2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mysentences_tf (
                id SERIAL PRIMARY KEY,
                sentence TEXT,
                embedding FLOAT[]
            );
        """)
        conn.commit()
        
        cur.execute("truncate table mysentences_tf")
        print("Table truncated successfully")

def insert_data(conn, model):
    with conn.cursor() as cur:
        for sentence in sentences:
            embedding = model([sentence])[0].numpy().tolist()
            cur.execute(
                "INSERT INTO mysentences_tf (sentence, embedding) VALUES (%s, %s)",
                (sentence, embedding)
            )
        conn.commit()

def search_a_match(conn, model, query):
    query_vec = model([query])[0].numpy().tolist()

    with conn.cursor() as cur:
        cur.execute("SELECT sentence, embedding FROM mysentences_tf")
        rows = cur.fetchall()

    best_sentence = None
    best_score = -1

    for sentence, embedding in rows:
        score = cosine_similarity(query_vec, embedding)
        if score > best_score:
            best_score = score
            best_sentence = sentence

    return best_sentence

if __name__ == "__main__":
    password = quote_plus(getpass("Enter your PostgreSQL password: "))
    config['password'] = password

    print("Loading model...")
    model = load_model()
    print("Model loaded.")

    with psycopg.connect(**config) as conn:
        print("Connected to PostgreSQL.")
        create_table(conn)
        insert_data(conn, model)
        result = search_a_match(conn, model, "What does the parrot do?")
        print(f'The closest match is: "{result}"')

