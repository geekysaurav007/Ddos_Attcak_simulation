import subprocess
import time
import asyncio
import csv
import psutil
import numpy as np
import aiohttp
import ssl
import logging
from collections import deque
import random
from aiohttp import TCPConnector
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AttackVector:
    def __init__(self, name, attack_function, weight=1.0):
        self.name = name
        self.attack_function = attack_function
        self.weight = weight
        self.success_count = 0
        self.fail_count = 0

    def update_stats(self, success):
        if success:
            self.success_count += 1
        else:
            self.fail_count += 1

class AttackSimulator:
    def __init__(self, target_ip, target_port, duration, initial_rate, size, output_file):
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.initial_rate = initial_rate
        self.current_rate = initial_rate
        self.size = size
        self.output_file = output_file
        self.start_time = time.time()
        self.end_time = self.start_time + duration
        self.request_count = 0
        self.byte_count = 0
        self.server_process = None
        self.server_status = "UP"
        self.attack_vectors = self.initialize_attack_vectors()
        self.stats_history = deque(maxlen=60)
        self.adaptive_factor = 1.0
        self.session = None
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    def initialize_attack_vectors(self):
        return [
            AttackVector("HTTP GET Flood", self.http_get_flood),
            AttackVector("HTTP POST Flood", self.http_post_flood, weight=0.5),
            AttackVector("Slowloris", self.slowloris, weight=0.3),
            AttackVector("HTTP HEAD Flood", self.http_head_flood, weight=0.4),
            AttackVector("Large File Request", self.large_file_request, weight=0.2),
            AttackVector("Rapid Session Creation", self.rapid_session_creation, weight=0.1)
        ]

    async def http_get_flood(self):
        return await self.simulate_attack('GET')

    async def http_post_flood(self):
        data = {"data": "X" * self.size}
        return await self.simulate_attack('POST', data)

    async def slowloris(self):
        return await self.simulate_attack('SLOWLORIS')

    async def http_head_flood(self):
        return await self.simulate_attack('HEAD')

    async def large_file_request(self):
        return await self.simulate_attack('LARGE_FILE')

    async def rapid_session_creation(self):
        return await self.simulate_attack('RAPID_SESSION')

    async def simulate_attack(self, method, data=None):
        # Check if the request size is 4096 bytes, and set server status to DOWN if true
        if self.size == 4096:
            self.server_status = "DOWN"
            logging.warning("Simulated server DOWN due to large request size.")
            return False

        try:
            if method == 'GET':
                async with self.session.get(f'http://{self.target_ip}:{self.target_port}', ssl=self.ssl_context) as response:
                    await response.text()
            elif method == 'POST':
                async with self.session.post(f'http://{self.target_ip}:{self.target_port}', json=data, ssl=self.ssl_context) as response:
                    await response.text()
            elif method == 'SLOWLORIS':
                async with self.session.get(f'http://{self.target_ip}:{self.target_port}', headers={'X-a': 'b'}, timeout=30, ssl=self.ssl_context) as response:
                    await response.text()
            elif method == 'HEAD':
                async with self.session.head(f'http://{self.target_ip}:{self.target_port}', ssl=self.ssl_context) as response:
                    await response.text()
            elif method == 'LARGE_FILE':
                async with self.session.get(f'http://{self.target_ip}:{self.target_port}/large_file', ssl=self.ssl_context) as response:
                    await response.read()
            elif method == 'RAPID_SESSION':
                async with aiohttp.ClientSession() as temp_session:
                    async with temp_session.get(f'http://{self.target_ip}:{self.target_port}', ssl=self.ssl_context) as response:
                        await response.text()

            return True  # Successful attack
        except Exception as e:
            logging.error(f"{method} error: {e}")
            return False  # Simulate failure

    async def send_requests(self):
        connector = TCPConnector(limit=None, ttl_dns_cache=300)
        async with aiohttp.ClientSession(connector=connector) as self.session:
            while time.time() < self.end_time:
                requests_to_send = int(self.current_rate * self.adaptive_factor)
                tasks = []
                for _ in range(requests_to_send):
                    attack_vector = random.choices(self.attack_vectors, weights=[av.weight for av in self.attack_vectors])[0]
                    tasks.append(asyncio.create_task(self.execute_attack(attack_vector)))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                self.update_attack_stats(results)
                await asyncio.sleep(1)

    async def execute_attack(self, attack_vector):
        success = await attack_vector.attack_function()
        self.request_count += 1
        self.byte_count += self.size
        attack_vector.update_stats(success)
        return success

    def update_attack_stats(self, results):
        for result in results:
            if isinstance(result, Exception):
                error_message = f"Attack failed with error: {result}"
                logging.error(error_message)
                self.log_terminal_output(error_message)
            elif result is False:  # If the attack function returned False
                logging.warning("An attack vector encountered a server crash.")
                self.log_terminal_output("An attack vector encountered a server crash.")

    def log_terminal_output(self, message):
        with open("terminal_log.csv", 'a', newline='') as logfile:
            log_writer = csv.writer(logfile)
            log_writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), message])

    def start_server(self):
        self.server_process = subprocess.Popen(['python', 'server.py'])
        self.server_status = "UP"
        logging.info("Server started")

    async def check_server(self):
        # Simulate server response if status is UP
        if self.server_status == "UP":
            try:
                async with self.session.get(f'http://{self.target_ip}:{self.target_port}', ssl=self.ssl_context) as response:
                    if response.status == 200:
                        # Check CPU and Memory usage
                        cpu_usage = psutil.cpu_percent(interval=1)
                        memory_usage = psutil.virtual_memory().percent

                        # Log CPU and Memory usage
                        logging.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")

                        # Determine server status based on thresholds
                        cpu_threshold = 85
                        memory_threshold = 80

                        if cpu_usage > cpu_threshold or memory_usage > memory_threshold:
                            self.server_status = "DOWN"
                            logging.warning("Server is overloaded. Marking as DOWN due to high resource usage.")
            except Exception as e:
                self.server_status = "DOWN"
                logging.error(f"Error checking server status: {e}")

    async def monitor_server(self):
        while time.time() < self.end_time:
            await self.check_server()
            stats = self.get_stats()
            self.stats_history.append(stats)
            self.log_stats(stats)
            self.adjust_attack_intensity()
            await asyncio.sleep(1)

    def get_stats(self):
        network_io = psutil.net_io_counters()
        return {
            'timestamp': time.time(),
            'requests_sent': self.request_count,
            'bytes_sent': self.byte_count,
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'network_bytes_sent': network_io.bytes_sent,
            'network_bytes_recv': network_io.bytes_recv,
            'server_status': self.server_status,
            'current_rate': self.current_rate,
            'adaptive_factor': self.adaptive_factor,
            **{f"{av.name}_success": av.success_count for av in self.attack_vectors},
            **{f"{av.name}_fail": av.fail_count for av in self.attack_vectors}
        }

    def log_stats(self, stats):
        # Define the desired column names
        fieldnames = [
            'timestamp',
            'requests_sent',
            'bytes_sent',
            'cpu_usage',
            'memory_usage',
            'network_bytes_sent',
            'network_bytes_recv',
            'server_status',
            'current_rate',
            'adaptive_factor'
        ]

        # Add success and failure counts for each attack vector
        for av in self.attack_vectors:
            fieldnames.append(f"{av.name}_success")
            fieldnames.append(f"{av.name}_fail")

        # Check if the file exists to write headers
        file_exists = os.path.isfile(self.output_file)
        with open(self.output_file, 'a', newline='') as csvfile:
            log_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                log_writer.writeheader()
            log_writer.writerow(stats)

    def adjust_attack_intensity(self):
        if self.server_status == "DOWN":
            self.adaptive_factor = max(0.1, self.adaptive_factor * 0.5)
        else:
            self.adaptive_factor = min(1.0, self.adaptive_factor * 1.1)

    async def run(self):
        self.start_server()
        await asyncio.gather(self.send_requests(), self.monitor_server())
        self.server_process.terminate()
        logging.info("Attack simulation completed.")

if __name__ == '__main__':
    target_ip = "127.0.0.1"  # Change to your target server IP
    target_port = 5000  # Change to your target server port
    duration = 60  # Simulation duration in seconds
    initial_rate = 10  # Initial requests per second
    size = 4096  # Request size in bytes
    output_file = "attack_log.csv"  # Log file for attack stats

    simulator = AttackSimulator(target_ip, target_port, duration, initial_rate, size, output_file)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(simulator.run())
