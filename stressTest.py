import json
from locust import HttpUser, task, between, LoadTestShape
import random
import time
import logging
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_endpoint(self):
        with open('property_ids.json') as f:
            propertyData = json.load(f)
        with open('agency_ids.json') as f:
            agencyData = json.load(f)

        property_id = random.choice(propertyData['properties'])['id']
        agency_id = random.choice(agencyData['users_agencies'])['id']

        self.client.post("/property", json={"propertyId": property_id})
        self.client.post("/properties", json={"agencyId": agency_id})
        self.client.post("/agency", json={"agencyId": agency_id})

class StressTest(LoadTestShape):
    stages = []
    for i in range(10):
        users = (i + 1) * 30
        spawn_rate = users // 10
        stages.append({"duration": i * 60, "users": users, "spawn_rate": spawn_rate})

    def tick(self):
        total_duration = sum(stage["duration"] for stage in self.stages)
        run_time = self.get_run_time()
        time_left = total_duration - run_time

        for i, stage in enumerate(self.stages):
            if run_time < stage["duration"]:
                logging.info(
                    f"{Fore.GREEN}Current Stage: {stage} - {len(self.stages) - i - 1} stages left - "
                    f"{Fore.BLUE}{int(stage['duration'] - run_time)} SECONDS LEFT IN STAGE - {Fore.RED}{int(time_left)} TOTAL SECONDS LEFT"
                )
                return stage["users"], stage["spawn_rate"]

        logging.info(f"{Fore.RED}No more stages")
        return None

