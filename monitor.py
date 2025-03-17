import argparse
import asyncio
import json
import logging
import time
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import aiohttp
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
MONITOR_INTERVAL = 15
MIN_SUCCESS_STATUS_CODE = 200
MAX_SUCCESS_STATUS_CODE = 299


def validate_endpoint_config(endpoint: Dict[str, Any]) -> bool:
    if not endpoint.get("name") or not endpoint.get("url"):
        return False
    return True


# Function to load configuration from the YAML file
def load_config(file_path: str) -> Optional[list[Dict[str, Any]]]:
    """
    Load configuration from a YAML file.
    Args:
        file_path (str): Path to the YAML configuration file.
    Returns:
        Optional[list[Dict[str, Any]]]: List of endpoints if successful, None otherwise.
    """
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)

            for endpoint in config:
                if not validate_endpoint_config(endpoint):
                    logger.error(f"Invalid endpoint configuration: name or url missing")
                    return None

            return config

    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        return None
    except yaml.YAMLError:
        logger.error(f"Error parsing YAML file: {file_path}")
        return None


def parse_domain(url: str) -> str:
    """
    Parse the domain from a URL.
    Args:
        url (str): The URL to parse.
    Returns:
        str: The domain name.
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    return domain.split(":")[0]


# Function to perform health checks
async def check_health(
    session: aiohttp.ClientSession, endpoint: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Perform a health check on the given endpoint.
    Args:
        session (aiohttp.ClientSession): The session to use for the request.
        endpoint (Dict[str, Any]): The endpoint to check.
    Returns:
        Tuple[str, str]: A tuple containing the status and domain.
    """
    name = endpoint["name"]
    url = endpoint["url"]  # Always a valid URL
    domain = parse_domain(url)
    method = endpoint.get("method", "GET").upper()  # Default to GET if not specified
    headers = endpoint.get("headers", {})
    body = json.loads(endpoint.get("body", "{}"))  # Always a valid JSON object

    start_time = time.time()

    try:
        async with session.request(
            method, url, headers=headers, json=body, timeout=REQUEST_TIMEOUT
        ) as response:
            response_time = time.time() - start_time

            if (
                MIN_SUCCESS_STATUS_CODE <= response.status <= MAX_SUCCESS_STATUS_CODE
                and response_time <= REQUEST_TIMEOUT
            ):
                logger.info(
                    f"Endpoint '{name}' is UP (Status Code: {response.status}, Response Time: {response_time:.3f}s)"
                )
                return "UP", domain
            else:
                reason = (
                    f"Response time exceeded {REQUEST_TIMEOUT * 1000}ms"
                    if response_time > REQUEST_TIMEOUT
                    else f"Status code: {response.status}"
                )
                logger.info(f"Endpoint '{name}' is DOWN ({reason})")
                return "DOWN", domain
    except asyncio.TimeoutError:
        logger.info(
            f"Endpoint '{name}' is DOWN (Response time exceeded {REQUEST_TIMEOUT * 1000}ms)"
        )
        return "DOWN", domain
    except Exception as e:
        logger.error(f"Endpoint '{name}' is DOWN (Exception: {str(e)})")
        return "DOWN", domain


# Function to check all endpoints in parallel
async def check_all_endpoints(endpoints: list[Dict[str, Any]]) -> list[Tuple[str, str]]:
    """
    Check all endpoints in parallel using asyncio.

    Args:
        endpoints (list[Dict[str, Any]]): List of endpoint configurations.

    Returns:
        list[Tuple[str, str]]: List of (status, domain) tuples.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [check_health(session, endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks)


# Main function to monitor endpoints
async def monitor_endpoints(file_path: str) -> None:
    """
    Monitor the availability of endpoints based on a YAML configuration file.
    Args:
        file_path (str): Path to the YAML configuration file.
    """
    config = load_config(file_path)
    if not config:
        return

    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        start_time = time.time()

        results = await check_all_endpoints(config)

        for status, domain in results:
            domain_stats[domain]["total"] += 1
            if status == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            logger.info(f"{domain} has {availability}% availability percentage")

        elapsed_time = time.time() - start_time
        sleep_time = max(MONITOR_INTERVAL - elapsed_time, 0)
        logger.info("---")
        time.sleep(sleep_time)


# Entry point of the program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor the availability of endpoints based on a YAML configuration file.",
    )
    parser.add_argument(
        "config_file", type=str, help="Path to the YAML configuration file."
    )

    args = parser.parse_args()

    try:
        asyncio.run(monitor_endpoints(args.config_file))
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user.")
