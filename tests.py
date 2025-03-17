from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import aiohttp
import pytest

from monitor import (REQUEST_TIMEOUT, check_health, load_config, parse_domain,
                     validate_endpoint_config)


def test_yaml_endpoint_config():
    """
    Test that the YAML endpoint config is loaded correctly.
    """
    mock_config = """
    - name: test endpoint
      url: http://example.com
      method: GET
      headers:
        content-type: application/json
      body: '{}'
    """
    # https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
    with patch("builtins.open", mock_open(read_data=mock_config)):
        config = load_config("config.yaml")

    assert config is not None
    assert config == [
        {
            "name": "test endpoint",
            "url": "http://example.com",
            "method": "GET",
            "headers": {"content-type": "application/json"},
            "body": "{}",
        }
    ]


def test_invalid_yaml_endpoint_config():
    """
    Test that an invalid YAML endpoint config is handled.
    """
    mock_config = """
    - name: test endpoint
      url, http://example.com
    """
    # https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
    with patch("builtins.open", mock_open(read_data=mock_config)):
        config = load_config("config.yaml")

    assert config is None


def test_missing_yaml_file():
    """
    Test that a missing YAML file is handled.
    """
    # https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth
    with patch("builtins.open", side_effect=FileNotFoundError):
        config = load_config("missing.yaml")

    assert config is None


@pytest.mark.asyncio
async def test_json_body_decoding():
    endpoint = {
        "name": "test endpoint",
        "url": "http://example.com",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": '{"key": "value"}',
    }

    # https://stackoverflow.com/questions/60142034/testing-and-mocking-asynchronous-code-that-uses-async-with-statement
    mock_response = MagicMock()
    mock_response.status = 200

    mock_request = AsyncMock()
    mock_request.__aenter__ = AsyncMock(return_value=mock_response)
    mock_request.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.request.return_value = mock_request

    status, domain = await check_health(mock_session, endpoint)

    assert status == "UP"
    assert domain == parse_domain(endpoint["url"])

    mock_session.request.assert_called_once_with(
        endpoint["method"].upper(),
        endpoint["url"],
        headers=endpoint["headers"],
        json={"key": "value"},
        timeout=REQUEST_TIMEOUT,
    )


@pytest.mark.asyncio
async def test_method_default_get():
    endpoint = {
        "name": "test endpoint",
        "url": "http://example.com",
        "body": "{}",
    }

    # https://stackoverflow.com/questions/60142034/testing-and-mocking-asynchronous-code-that-uses-async-with-statement
    mock_response = MagicMock()
    mock_response.status = 200

    mock_request = AsyncMock()
    mock_request.__aenter__ = AsyncMock(return_value=mock_response)
    mock_request.__aexit__ = AsyncMock(return_value=False)

    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.request.return_value = mock_request

    status, domain = await check_health(mock_session, endpoint)

    assert status == "UP"
    assert domain == parse_domain(endpoint["url"])

    mock_session.request.assert_called_once_with(
        "GET",
        endpoint["url"],
        headers={},
        json={},
        timeout=REQUEST_TIMEOUT,
    )


def test_parse_domain():
    """
    Test that the parse_domain function only returns the domain without the port.
    """
    url = "http://example.com:443/body"
    domain = parse_domain(url)

    assert domain == "example.com"


def test_validate_endpoint_config():
    endpoint = {
        "name": "test endpoint",
        "url": "http://example.com",
    }

    assert validate_endpoint_config(endpoint)


def test_invalid_endpoint_config():
    endpoint = {
        "url": "http://example.com",
    }
    assert not validate_endpoint_config(endpoint)


if __name__ == "__main__":
    pytest.main()
