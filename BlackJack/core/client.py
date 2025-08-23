import requests
import yaml

with open("data/config.yaml", "r") as f:
    config = yaml.safe_load(f)

BASE_URL = config["base_url"]

class APIClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def get(self, endpoint, **kwargs):
        return self.session.get(f"{self.base_url}{endpoint}", **kwargs)

    def post(self, endpoint, json=None, **kwargs):
        return self.session.post(f"{self.base_url}{endpoint}", json=json, **kwargs)