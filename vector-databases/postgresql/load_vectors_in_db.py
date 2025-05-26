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
'Go to Try IBM watsonx.ai or Try watsonx.governance. If you sign up for watsonx.governance, you automatically provision watsonx.ai as well.',
'Yes, when you sign up for IBM watsonx.ai, you automatically provision the free version of the underlying services: Watson Studio, Watson Machine Learning, and IBM Cloud Object Storage. When you sign up for IBM watsonx.governance, you automatically provision the free version of Watson OpenScale and the free versions of the services for IBM watsonx.ai.',
'When you are ready to upgrade any of the underlying services for watsonx.ai or watsonx.governance, you can upgrade in place without losing any of your work or data. You must be the owner or administrator of the IBM Cloud account for a service to upgrade it. See Upgrading services on watsonx.'
]

# Function to pad or truncate a list to length 100
def pad_array(array, length=100):
    return array[:length] + [0] * max(0, length - len(array))

# Function to convert a sentence into a fixed-length array of ASCII codes
def vectorize(sentence):
    return pad_array([ord(char) for char in sentence])

if __name__ == "__main__":
    password = quote_plus(getpass("Enter your PostgreSQL password: "))
    config['password'] = password

    try:
        with psycopg.connect(**config) as conn:
            with conn.cursor() as cur:
                print("Connected to PostgreSQL database")

                # Create table if it doesn't exist
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS mynewsentences (
                        id SERIAL PRIMARY KEY,
                        sentence TEXT,
                        embedding INTEGER[]
                    );
                """
                cur.execute(create_table_query)
                print("Table created successfully")
        
                cur.execute("truncate table mysentences")
                print("Table truncated successfully")

                # Insert sentences and their embeddings
                for sentence in sentences:
                    embedding = vectorize(sentence)
                    cur.execute(
                        "INSERT INTO mynewsentences (sentence, embedding) VALUES (%s, %s);",
                        (sentence, embedding)
                    )

                # Fetch and print all rows
                cur.execute("SELECT * FROM mynewsentences;")
                rows = cur.fetchall()
                for row in rows:
                    print(row[1])  # sentence

    except Exception as e:
        print(f"Error: {e}")
