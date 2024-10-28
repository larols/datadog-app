from flask import Flask, jsonify, request
from ddtrace import patch_all, patch, tracer
import logging
import psycopg2
import os
import uuid
from datetime import datetime
import requests

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
    visit_time = datetime.now()  # Get the current timestamp as a datetime object

    try:
        # Store the UID in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (uid, visit_time) VALUES (%s, %s);",
                       (uid, visit_time))  # Use the datetime object
        conn.commit()

        # Check the number of entries and delete the oldest if necessary
        cursor.execute("SELECT COUNT(*) FROM visitors;")
        count = cursor.fetchone()[0]
        if count > MAX_ENTRIES:
            cursor.execute("""
                DELETE FROM visitors
                WHERE ctid IN (
                    SELECT ctid
                    FROM visitors
                    ORDER BY visit_time ASC
                    LIMIT 1
                );
            """)  # Remove the oldest entry

        cursor.close()
        conn.close()

        log.info(f"Visit recorded: {uid}")  # Log the recorded visit
        return jsonify({"message": "Visit recorded successfully!", "uid": uid}), 201
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/uid/latest', methods=['GET'])
def fetch_latest_uid():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT uid, visit_time FROM visitors ORDER BY visit_time DESC LIMIT 1;")
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            latest_uid, visit_time = row
            log.info("Fetched latest UID from the database")  # Log the fetching action
            return jsonify({"uid": str(latest_uid), "visit_time": str(visit_time)}), 200
        else:
            return jsonify({"error": "No UID found"}), 404
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

# Vulnerable delete endpoint to test Datadog Code Vulnerability Detection
@app.route('/api/uid/delete', methods=['POST'])
def delete_uid():
    ctid = request.args.get('ctid', '0')  # Insecure way to get 'ctid' for deletion

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM visitors WHERE ctid = '{ctid}';")  # Directly inserting user input
        conn.commit()
        cursor.close()
        conn.close()

        log.info("Deleted UID with user-provided ctid")  # Log deletion
        return jsonify({"message": "UID deleted successfully!"}), 200
    except Exception as e:
        log.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/uid/ssrf', methods=['POST'])
def ssrf():
    target_url = request.json.get('url', '')  # User-provided URL
    try:
        response = requests.get(target_url)  # This can lead to SSRF
        return jsonify({"data": response.text}), 200
    except Exception as e:
        log.error(f"Error fetching URL: {e}")
        return jsonify({"error": "Failed to fetch URL"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
