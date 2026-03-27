"""Unit tests for ocr/vision_client.py."""
import json
from unittest.mock import MagicMock, patch

import pytest

from words_maker.ocr.vision_client import detect_text


class TestDetectText:
    @pytest.mark.unit
    def test_extracts_text_from_response(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "responses": [
                {
                    "textAnnotations": [
                        {"description": "Hello World"},
                        {"description": "Hello"},
                        {"description": "World"},
                    ]
                }
            ]
        }

        with patch("words_maker.ocr.vision_client.requests.post", return_value=mock_response):
            result = detect_text(b"fake_image", "fake_api_key")

        assert result == "Hello World"

    @pytest.mark.unit
    def test_returns_empty_on_api_error(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        with patch("words_maker.ocr.vision_client.requests.post", return_value=mock_response):
            result = detect_text(b"fake_image", "bad_key")

        assert result == ""

    @pytest.mark.unit
    def test_returns_empty_on_no_text(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"responses": [{}]}

        with patch("words_maker.ocr.vision_client.requests.post", return_value=mock_response):
            result = detect_text(b"blank_image", "key")

        assert result == ""
