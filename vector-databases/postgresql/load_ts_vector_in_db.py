import psycopg
from psycopg import sql
from urllib.parse import quote_plus
from getpass import getpass

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


def add_data(conn):
    print("Connected to PostgreSQL database")

    # Create table if not exists
    create_table_query = """
        CREATE TABLE IF NOT EXISTS mysentences (
            id SERIAL PRIMARY KEY,
            sentence tsvector,
            actual_sentence TEXT
        );
    """

    with conn.cursor() as cur:
        cur.execute(create_table_query)
        print("Table created successfully")
        
        cur.execute("truncate table mysentences")
        print("Table truncated successfully")

        # Insert sentences
        for sentence in sentences:
            cur.execute(
                "INSERT INTO mysentences (sentence, actual_sentence) VALUES (to_tsvector('english', %s), %s)",
                (sentence, sentence)
            )

        # Fetch all rows
        cur.execute("SELECT * FROM mysentences;")
        rows = cur.fetchall()
        for row in rows:
            print(f"{row[2]}   {row[1]}")  # actual_sentence and tsvector


def get_data(conn, str_query):
    print("Running full-text search query")

    with conn.cursor() as cur:
        cur.execute(
            "SELECT actual_sentence FROM mysentences WHERE sentence @@ to_tsquery('english', %s);",
            (str_query,)
        )
        results = cur.fetchall()
        for row in results:
            print(row[0])


if __name__ == "__main__":
    password = quote_plus(getpass("Enter your PostgreSQL password: "))
    config['password'] = password

    try:
        with psycopg.connect(**config) as conn:
            add_data(conn)
            get_data(conn, "penguin")
    except Exception as e:
        print(f"Error: {e}")

