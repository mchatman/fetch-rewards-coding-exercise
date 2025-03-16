from unittest.mock import patch

from monitor import check_health


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