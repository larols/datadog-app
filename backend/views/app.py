from flask import Flask, jsonify

app = Flask(__name__)

# Initialize a visit counter
visit_count = 0

@app.route('/api/views', methods=['GET'])  # Updated endpoint to /api/views
def get_views_data():
    global visit_count
    visit_count += 1  # Increment the visit counter
    
    data = {
        "id": 1,
        "text": f"Views: You are visitor number {visit_count}!"  # Updated text to reflect the new endpoint
    }
    return jsonify(data)

@app.route('/api/visits', methods=['GET'])
def get_visit_count():
    return jsonify({"visit_count": visit_count})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Expose the app on port 5000