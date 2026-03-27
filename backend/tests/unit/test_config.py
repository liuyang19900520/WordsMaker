"""Unit tests for config.py."""
import os

import pytest

from words_maker.config import load_config


class TestLoadConfig:
    @pytest.mark.unit
    def test_missing_google_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.setenv("EUDIC_COOKIE", "test_cookie")
        with pytest.raises(KeyError):
            load_config()

    @pytest.mark.unit
    def test_missing_eudic_cookie_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
        monkeypatch.delenv("EUDIC_COOKIE", raising=False)
        with pytest.raises(KeyError):
            load_config()

    @pytest.mark.unit
    def test_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "key123")
        monkeypatch.setenv("EUDIC_COOKIE", "cookie_val")
        monkeypatch.delenv("DYNAMODB_TABLE_NAME", raising=False)
        monkeypatch.delenv("AWS_REGION", raising=False)
        monkeypatch.delenv("PDF_START_PAGE", raising=False)
        monkeypatch.delenv("PDF_END_PAGE", raising=False)

        config = load_config()
        assert config.dynamodb_table_name == "words_maker"
        assert config.aws_region == "ap-northeast-1"
        assert config.pdf_start_page == 1
        assert config.pdf_end_page == 15
        assert config.aws_access_key_id is None

    @pytest.mark.unit
    def test_custom_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GOOGLE_API_KEY", "gkey")
        monkeypatch.setenv("EUDIC_COOKIE", "cookie")
        monkeypatch.setenv("DYNAMODB_TABLE_NAME", "my_table")
        monkeypatch.setenv("PDF_START_PAGE", "3")
        monkeypatch.setenv("PDF_END_PAGE", "20")

        config = load_config()
        assert config.dynamodb_table_name == "my_table"
        assert config.pdf_start_page == 3
        assert config.pdf_end_page == 20
