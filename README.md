# Fetch Rewards Coding Exercise

This tool monitors the availability of HTTP endpoints based on a YAML configuration file. It provides cumulative availability metrics by domain and logs the results at a 15 second interval.

## Installation

1. Clone the repository
```bash
git clone https://github.com/mchatman/fetch-rewards-coding-exercise.git
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

## Usage

```bash
python monitor.py <config_file_path>
```

## Configuration

The configuration file should be a YAML file with the following format:
```yaml
- name: <endpoint_name>
  url: <endpoint_url>
  method: <http_method> # Optional, defaults to GET
  headers: <headers> # Optional
  body: <body> # Optional
```

## Issues Identified and Changes Made

### 1. Deserialize JSON body failure
**Issue:**The `body` field in the configuration was not being deserialized as JSON before being passed to the `requests` library.

**Fix:**Deserialized the `body` field as JSON using the json library before passing it to the `requests` library.
