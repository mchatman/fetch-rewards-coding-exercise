import json
import logging
import time
from collections import defaultdict

import requests
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 0.5  # Default timeout is 0.5 seconds (500ms)


# Function to load configuration from the YAML file
def load_config(file_path):
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        return None
    except yaml.YAMLError:
        logger.error(f"Error parsing YAML file: {file_path}")
        return None


# Function to perform health checks
def check_health(endpoint):
    name = endpoint["name"]
    url = endpoint["url"]  # Always a valid URL
    method = endpoint.get("method", "GET")  # Default to GET if not specified
    headers = endpoint.get("headers", {})
    body = json.loads(endpoint.get("body", "{}"))  # Always a valid JSON object

    start_time = time.time()

    try:
        response = requests.request(
            method=method, url=url, headers=headers, json=body, timeout=1.0
        )

        response_time = time.time() - start_time

        if 200 <= response.status_code < 300 and response_time <= REQUEST_TIMEOUT:
            logger.info(
                f"Endpoint '{name}' is UP (Status Code: {response.status_code}, Response Time: {response_time:.3f}s)"
            )
            return "UP"
        else:
            reason = (
                f"Response time exceeded {REQUEST_TIMEOUT * 1000}ms"
                if response_time > REQUEST_TIMEOUT
                else f"Status code: {response.status_code}"
            )
            logger.info(f"Endpoint '{name}' is DOWN ({reason})")
            return "DOWN"
    except requests.RequestException:
        return "DOWN"


# Main function to monitor endpoints
def monitor_endpoints(file_path):
    config = load_config(file_path)
    if not config:
        return

    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        for endpoint in config:
            domain = endpoint["url"].split("//")[-1].split("/")[0]
            result = check_health(endpoint)

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            logger.info(f"{domain} has {availability}% availability percentage")

        logger.info("---")
        time.sleep(15)


# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        logger.error("Usage: python monitor.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user.")
