from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

# Variable to track server status
server_status = "UP"

@app.route('/')
def index():
    # Return server status
    if server_status == "DOWN":
        return jsonify({"status": server_status, "message": "Server is down."}), 500
    return jsonify({"status": server_status}), 200

@app.route('/', methods=['POST'])
def process_request():
    global server_status
    # Get the size of the incoming data
    data_size = request.content_length

    # Check if the incoming request size is 4096 bytes
    if data_size >= 3000:
        server_status = "DOWN"  # Set server status to DOWN
        return jsonify({"message": "Simulated crash due to request size of 4096 bytes!"}), 500
    
    # Simulate processing time
    time.sleep(random.uniform(0.1, 1.0))
    return jsonify({"message": "Processed successfully!"}), 200

@app.route('/large_file')
def large_file():
    time.sleep(2)  # Simulate delay for large file
    return "This is a large file response.", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
