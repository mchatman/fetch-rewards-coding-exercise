# Fetch Rewards Coding Exercise

This tool monitors the availability of HTTP endpoints based on a YAML configuration file. It provides cumulative availability metrics by domain and logs the results at a 15 second interval.

## Installation

1. Clone the repository
```bash
git clone https://github.com/mchatman/fetch-rewards-coding-exercise.git
cd fetch-rewards-coding-exercise
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate (on Linux/Mac)
.\venv\Scripts\activate (on Windows)
```

3. Install required dependencies
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

## Testing

1. Run tests
```bash
python -m pytest tests.py
```

## Issues Identified and Changes Made

### 1. Deserialize JSON body failure
**Issue:**The `body` field in the configuration was not being deserialized as JSON before being sent in a HTTP request.

**Fix:**Deserialized the `body` field as JSON before sending it in a HTTP request.

### 2. Default method not specified
**Issue:**The `method` field may not be specified, so the default method was not being used when sending the HTTP request.

**Fix:**Specified the default method as GET in the method variable.

### 3. Handle invalid YAML endpoint config
**Issue:**The `load_config` function did not handle invalid YAML endpoint configs.

**Fix:**Added error handling for invalid YAML endpoint configs.

### 4. Replaced print statements with logging
**Issue:**The script used `print()` statements for output which lacked log severity levels.

**Fix:**Replaced all print statements with logging including log levels and structured output.

### 5. Removes port from domain
**Issue:**The `parse_domain` function did not handle removing ports in the URL, causing the same domain to be counted separately.

**Fix:**Created the `parse_domain` function to remove ports from the URL.

### 6. Logs availability duration accuracy
**Issue:**The `monitor_endpoints` function did not log the availability duration exactly at 15 seconds. Sleep time did not account for the time taken to process the endpoints.

**Fix:**Fixed the `monitor_endpoints` function to log the availability duration accurately by accounting for the time taken to process the endpoints.

### 7. Validate endpoint config
**Issue:**The `load_config` function did not validate the endpoint config which may cause a KeyError for required fields that are missing.

**Fix:**Added validation for the `name` and `url` fields in the `load_config` function. If either is missing, logs the missing fields and returns None.

### 8. Improved command line interface
**Issue:**The command-line interface did not allow for customization of monitoring parameters and a help message.

**Fix:**Added a help message and allowed customization of monitoring parameters using argparse.