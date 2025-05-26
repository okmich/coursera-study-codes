import psycopg
from getpass import getpass
from urllib.parse import quote_plus


config = {
    "host": "localhost",
    "dbname": "postgres",
    "port": 5432
}

def get_postgres_connection():
    user = input("Enter your PostgreSQL username: ")
    password = quote_plus(getpass("Enter your PostgreSQL password: "))
    host = "localhost"
    port = 5432
    dbname = "postgres"

    conn_str = f"dbname={dbname} user={user} password={password} host={host}"
    try:
        conn = psycopg.connect(conn_str)
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            if result and result[0] == 1:
                print("Successfully connected to PostgreSQL!")
        return conn
    except Exception as e:
        print(f"Connection failed: {e}")
        return None


if __name__ == "__main__":
    conn = get_postgres_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                result = cur.fetchone()
                if result and result[0] == 1:
                    print("Pinged your PostgreSQL server. Connection successful!")
        except Exception as e:
            print(f"Ping failed: {e}")
        finally:
            conn.close()
