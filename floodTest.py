import json
from locust import HttpUser, task, constant
import random

class APIUser(HttpUser):
    wait_time = constant(0)  # Nessuna attesa tra le richieste

    @task
    def flood_test(self):
        # Carica i property_ids.json
        with open('property_ids.json') as f:
            data = json.load(f)
        
        # Seleziona un ID di proprietà casuale
        property_id = random.choice(data['properties'])['id']
        
        # Invia la richiesta al server
        self.client.post("/property", json={"property": property_id})
