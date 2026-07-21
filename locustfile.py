# locustfile.py
from locust import HttpUser, task, between

class TravelKeetUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat(self):
        self.client.post("/chat", json={"message": "Plan a 3-day campervan trip for two."})