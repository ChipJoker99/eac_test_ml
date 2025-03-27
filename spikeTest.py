import json
import random
import logging
import argparse
from locust import HttpUser, task, between, LoadTestShape, events
import subprocess
from statistics import mean
import csv
import time

def record_metrics(endpoint, response_time, status_code):
    # Se il file non esiste, scrivi anche l'intestazione
    file_exists = False
    try:
        with open("ml_performance_data.csv", "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open("ml_performance_data.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "endpoint", "response_time", "status_code"])
        writer.writerow([time.time(), endpoint, response_time, status_code])

# Configura il logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configura il logger per scrivere su console e su file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Aggiunge un file handler
file_handler = logging.FileHandler('performance_analysis.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Parsing dei parametri da terminale
parser = argparse.ArgumentParser(description="Configurazione dello Spike Test")
parser.add_argument("--duration", type=int, default=60, help="Durata del test in secondi")
parser.add_argument("--max_users", type=int, default=500, help="Numero massimo di utenti simultanei")
parser.add_argument("--spawn_rate", type=int, default=50, help="Tasso di crescita degli utenti")
args, unknown = parser.parse_known_args()

class APIUser(HttpUser):
    wait_time = between(0.5, 1)
    endpoints = ["/property", "/agency", "/properties"]

    @task
    def spike_test(self):
        with open('property_ids.json') as f:
            propertyData = json.load(f)
        with open('agency_ids.json') as f:
            agencyData = json.load(f)
        
        property_id = random.choice(propertyData['properties'])['id']
        agency_id = random.choice(agencyData['users_agencies'])['id']
        endpoint = random.choice(self.endpoints)
        payload = {"propertyId": property_id} if endpoint == "/property" else {"endpoint": endpoint, "agencyId": agency_id}
        
        response = self.client.post(endpoint, json=payload)
        
        # Registra il tempo di risposta e il risultato
        response_time = response.elapsed.total_seconds() * 1000  # conversione in millisecondi
        if not hasattr(self, "performance_analyzer"):
            # Istanzia il PerformanceAnalyzer la prima volta
            self.performance_analyzer = PerformanceAnalyzer()
        
        self.performance_analyzer.collect_data(response_time, response.status_code)
        if len(self.performance_analyzer.times) % 10 == 0:
            self.performance_analyzer.analyze()
        
        if response.status_code == 200:
            logger.info(f"✅ Success [{response.status_code}] - Endpoint: {endpoint} - Property ID: {property_id}")
        else:
            logger.error(f"❌ Error [{response.status_code}] - Endpoint: {endpoint}")

        response_time = response.elapsed.total_seconds() * 1000  # in ms
        record_metrics(endpoint, response_time, response.status_code)


class SpikeLoad(LoadTestShape):
    stages = [
        {"duration": args.duration // 3, "users": args.max_users // 2, "spawn_rate": args.spawn_rate},
        {"duration": args.duration, "users": args.max_users, "spawn_rate": args.spawn_rate},
        {"duration": args.duration + 20, "users": args.max_users // 4, "spawn_rate": args.spawn_rate // 2},
    ]
    
    def __init__(self):
        super().__init__()
        self.response_times = []
    
    def tick(self):
        for stage in self.stages:
            if self.get_run_time() < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None
    
    def record_response_time(self, response_time):
        self.response_times.append(response_time)
        if len(self.response_times) % 10 == 0:
            avg_time = mean(self.response_times[-10:])
            logger.info(f"📊 Average Response Time (last 10 requests): {avg_time:.2f} ms")

# ML-based Performance Analysis (Facoltativo)
try:
    from sklearn.linear_model import LinearRegression
    import numpy as np
    
    class PerformanceAnalyzer:
        def __init__(self):
            self.times = []
            self.failures = []
            self.model = LinearRegression()
        
        def collect_data(self, response_time, status_code):
            self.times.append(response_time)
            self.failures.append(1 if status_code != 200 else 0)
        
        def analyze(self):
            if len(self.times) > 10:
                X = np.array(self.times).reshape(-1, 1)
                y = np.array(self.failures)
                self.model.fit(X, y)
                trend = self.model.coef_[0]
                analysis_info = f"📈 ML Analysis: Failure Trend Coefficient: {trend:.5f}"
                
                # Scrive l'analisi su file
                with open("ml_analysis_results.txt", "a") as file:
                    file.write(analysis_info + "\n")
                
                logger.info(analysis_info)

except ImportError:
    logger.warning("⚠️ SciKit-Learn non installato, analisi ML disabilitata.")

@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    # Access the contents of kwargs
    print(kwargs)
    print(environment)
    # Avvia lo script di analisi ML una volta che il test termina
    subprocess.call(["python3", "ml_analysis.py"])
