from unittest.mock import patch, mock_open

from monitor import check_health, load_config


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


def test_json_body_decoding():
    endpoint = {
        "name": "test endpoint",
        "url": "http://example.com",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": '{"key": "value"}',
    }

    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 200
        result = check_health(endpoint)

        assert result == "UP"
        assert mock_request.call_args[1]["json"] == {"key": "value"}
        mock_request.assert_called_once_with(
            method=endpoint["method"],
            url=endpoint["url"],
            headers=endpoint["headers"],
            json={"key": "value"},
            timeout=1.0,
        )


def test_method_default_get():
    endpoint = {
        "name": "test endpoint",
        "url": "http://example.com",
        "body": '{}',
    }

    with patch("requests.request") as mock_request:
        mock_request.return_value.status_code = 200
        result = check_health(endpoint)

        assert result == "UP"
        assert mock_request.call_args[1]["method"] == "GET"

        mock_request.assert_called_once_with(
            method="GET",
            url=endpoint["url"],
            headers={},
            json={},
            timeout=1.0,
        )

if __name__ == "__main__":
    pytest.main()