import pandas as pd
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters - replace with your actual details
DB_HOST = os.getenv("HOST")
DB_NAME = os.getenv("DATABASE")
DB_USER = os.getenv("USERNAME")
DB_PASS = os.getenv("PASSWORD")
DB_PORT = os.getenv("PORT")

# Folder containing CSV files
DATA_FOLDER = 'data'

def create_table_if_not_exists(conn, table_name):
    """Create table if it doesn't exist."""
    create_query = sql.SQL("""
    CREATE TABLE IF NOT EXISTS {} (
        date DATE,
        open NUMERIC,
        high NUMERIC,
        low NUMERIC,
        close NUMERIC,
        volume NUMERIC,
        name VARCHAR(10)
    )
    """).format(sql.Identifier(table_name))
    
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

def load_csv_to_table(csv_file, table_name):
    """Load CSV data into PostgreSQL table."""
    # Read CSV into DataFrame
    df = pd.read_csv(csv_file)
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS, 
        port=DB_PORT
    )
    
    try:
        # Create table if not exists
        create_table_if_not_exists(conn, table_name)
        
        # Insert data row by row (for simplicity; use COPY for large datasets)
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                insert_query = sql.SQL("""
                INSERT INTO {} (date, open, high, low, close, volume, name)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """).format(sql.Identifier(table_name))
                cur.execute(insert_query, (
                    row['Date'], row['Open'], row['High'], row['Low'],
                    row['Close'], row['Volume'], row['Name']
                ))
        conn.commit()
        print(f"Data from {csv_file} loaded into table {table_name} successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error loading {csv_file}: {e}")
    finally:
        conn.close()

# Get all CSV files in the data folder
csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.csv')]

# Load each CSV into its table
for csv_file in csv_files:
    full_path = os.path.join(DATA_FOLDER, csv_file)
    table_name = os.path.splitext(csv_file)[0].lower()  # Remove .csv and make lowercase
    load_csv_to_table(full_path, table_name)