from flask import Flask, jsonify, request
from ddtrace import patch_all, patch
import logging
import time
import psycopg2
import os
import uuid
from datetime import datetime

@app.route('/api/uid', methods=['POST'])
def record_visit():
    uid = str(uuid.uuid4())  # Generate a unique identifier (UID)
    visit_time = datetime.now()  # Get the current timestamp as a datetime object

    try:
        # Store the UID in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (uid, visit_time) VALUES (%s, %s);",
                       (uid, visit_time))  # Now visit_time is a datetime object
        conn.commit()

        # Check the number of entries and delete the oldest if necessary
        cursor.execute("SELECT COUNT(*) FROM visitors;")
        count = cursor.fetchone()[0]
        if count > MAX_ENTRIES:
            cursor.execute("DELETE FROM visitors ORDER BY visit_time ASC LIMIT 1;")  # Remove the oldest entry

        cursor.close()
        conn.close()

        log.info(f"Visit recorded: {uid}")  # Log the recorded visit
        return jsonify({"message": "Visit recorded successfully!", "uid": uid}), 201
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

# Patch all supported libraries for Datadog tracing
patch_all()
patch(logging=True)  # Enable tracing for logging

# Initialize the Flask app
app = Flask(__name__)

# Define logging format including Datadog trace information
FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
          '[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
          '- %(message)s')

logging.basicConfig(format=FORMAT)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Database connection function
def get_db_connection():
    host = os.environ['POSTGRES_HOST']
    conn = psycopg2.connect(
        host=host,
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )
    return conn

# Validate required environment variables
required_env_vars = ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
for var in required_env_vars:
    if os.environ.get(var) is None:
        log.error(f"Missing environment variable: {var}")
        raise RuntimeError(f"Missing environment variable: {var}")

# Function to create the visitors table if it does not exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id SERIAL PRIMARY KEY,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            uid UUID DEFAULT gen_random_uuid()
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    log.info("Database initialized and tables created if they did not exist.")

# Initialize the database at startup
initialize_database()

# Set the maximum number of stored UIDs
MAX_ENTRIES = 100

@app.route('/api/uid', methods=['POST'])
def record_visit():
    uid = str(uuid.uuid4())  # Generate a unique identifier (UID)
    visit_time = time.time()  # Record the current timestamp

    try:
        # Store the UID in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (uid, visit_time) VALUES (%s, %s);",
                       (uid, visit_time))
        conn.commit()

        # Check the number of entries and delete the oldest if necessary
        cursor.execute("SELECT COUNT(*) FROM visitors;")
        count = cursor.fetchone()[0]
        if count > MAX_ENTRIES:
            cursor.execute("DELETE FROM visitors ORDER BY visit_time ASC LIMIT 1;")  # Remove the oldest entry

        cursor.close()
        conn.close()

        log.info(f"Visit recorded: {uid}")  # Log the recorded visit
        return jsonify({"message": "Visit recorded successfully!", "uid": uid}), 201
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/uid/fetch', methods=['GET'])
def fetch_uids():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT uid FROM visitors ORDER BY visit_time DESC;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        log.info("Fetched UIDs from the database")  # Log the fetching action
        return jsonify({"uids": [str(row[0]) for row in rows]}), 200
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)