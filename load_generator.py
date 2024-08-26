import requests
import time
import random

def generate_load():
    urls = ['http://flask-app-service/', 'http://flask-app-service/data']
    while True:
        url = random.choice(urls)
        try:
            response = requests.get(url)
            print(f"Requested {url}, Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request to {url} failed: {e}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == '__main__':
    generate_load()

