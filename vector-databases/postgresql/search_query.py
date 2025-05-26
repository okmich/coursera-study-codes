import psycopg
from psycopg import sql

import math
from urllib.parse import quote_plus
from getpass import getpass


# PostgreSQL connection configuration
config = {
    "host": "localhost",
    "dbname": "postgres",
    "port": 5432,
    "user": "test_user"
}

# Function to pad or truncate a list to length 100
def pad_array(array, length=100):
    return array[:length] + [0] * max(0, length - len(array))

# Convert sentence to fixed-length ASCII vector
def vectorize(sentence):
    return pad_array([ord(char) for char in sentence])

# Compute Euclidean distance between two vectors
def euclidean_distance(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))

# Main search function
def search_a_match(query_str):
    password = quote_plus(getpass("Enter your PostgreSQL password: "))
    config['password'] = password

    try:
        with psycopg.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT sentence, embedding FROM mynewsentences;")
                rows = cur.fetchall()

                query_vec = vectorize(query_str)
                for sentence, embedding in rows:
                    dist = euclidean_distance(embedding, query_vec)
                    print(f"Sentence: {sentence}")
                    print(f"Distance: {dist:.2f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_a_match("What is the horse doing??")
