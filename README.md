# DDoS Attack Simulation Project

This project simulates Distributed Denial of Service (DDoS) attacks to study server behavior and performance under different attack vectors. It consists of two main components:

- **`server.py`:** A Flask server simulating various responses to incoming requests, including crashes and delays.
- **`simple.py`:** A Python-based DDoS attack simulator that uses multiple attack strategies to stress-test the server.

---

## Features

1. **Server Simulation:**
   - Handles `GET`, `POST`, `HEAD`, and custom requests.
   - Simulates server crashes based on request size and resource usage.
   - Includes endpoints for large file downloads and delayed processing.

2. **Attack Simulation:**
   - Implements multiple attack vectors such as HTTP GET Flood, HTTP POST Flood, Slowloris, and others.
   - Dynamically adjusts attack intensity based on server status.
   - Logs CPU, memory, and network usage during attacks.

3. **Real-Time Monitoring:**
   - Tracks server status, resource usage, and attack metrics.
   - Saves detailed logs in CSV format for analysis.

---

## Prerequisites

1. **Python 3.8+**
2. Install dependencies:
   ```bash
   pip install flask aiohttp psutil numpy
   ```

---

## Setup and Usage

### Step 1: Start the Server
Run the Flask server to simulate endpoints:
```bash
python server.py
```

### Step 2: Run the Simulator
Execute the attack simulation with specified parameters:
```bash
python simple.py
```

### Simulation Parameters
- **`target_ip`**: IP address of the server (default: `127.0.0.1`).
- **`target_port`**: Port number of the server (default: `5000`).
- **`duration`**: Duration of the simulation in seconds (default: `60`).
- **`initial_rate`**: Initial requests per second (default: `10`).
- **`size`**: Size of the request payload in bytes (default: `4096`).
- **`output_file`**: Log file for attack statistics (default: `attack_log.csv`).

---

## Technical Details

### `server.py`
- **Endpoints:**
  - `GET /`: Returns server status (`UP` or `DOWN`).
  - `POST /`: Processes requests and simulates crashes for large payloads.
  - `GET /large_file`: Simulates a delayed large file response.

### `simple.py`
- **Attack Vectors:**
  - HTTP GET Flood
  - HTTP POST Flood
  - Slowloris
  - HTTP HEAD Flood
  - Large File Request
  - Rapid Session Creation

- **Dynamic Intensity:**
  - Reduces attack intensity when the server is overloaded.
  - Increases intensity when the server stabilizes.

- **Metrics Logged:**
  - Requests sent
  - Bytes transferred
  - CPU and memory usage
  - Network I/O
  - Success and failure counts for each attack vector

---

## Logs and Analysis
Logs are saved in CSV format (`attack_log.csv`) with the following details:
- Timestamp
- Requests sent
- Bytes sent
- CPU and memory usage
- Server status
- Attack vector success/failure statistics

Use the logs for detailed post-simulation analysis.

---

## Flowchart

