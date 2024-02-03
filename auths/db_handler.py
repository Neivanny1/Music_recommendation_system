from sqlalchemy import create_engine, text
import os

# db_uri.py
def get_db_uri():
    with open('creds', 'r') as file:
        return file.read().strip()
db_uri = get_db_uri()

#conecting to the databases;
engine = create_engine(db_uri)

#log in
def load_jobs_from_():
    with engine.connect() as conn:
        # Execute your SQL query
        result = conn.execute(text('SELECT * FROM accounts'))
        # Fetch column names from the result's keys
        column_names = result.keys()
        # Fetch all rows from the result
        rows = result.fetchall()
        # Convert each row to a dictionary
        jobs = [dict(zip(column_names, row)) for row in rows]
        return jobs
load = load_jobs_from_db()
print(load)