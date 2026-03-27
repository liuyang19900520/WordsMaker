"""Unit tests for eudic/client.py."""
import pytest

from words_maker.eudic.client import _parse_cookie_string, build_session


class TestParseCookieString:
    @pytest.mark.unit
    def test_simple_cookie(self) -> None:
        result = _parse_cookie_string("foo=bar; baz=qux")
        assert result == {"foo": "bar", "baz": "qux"}

    @pytest.mark.unit
    def test_value_with_equals(self) -> None:
        result = _parse_cookie_string("token=abc=def")
        assert result["token"] == "abc=def"

    @pytest.mark.unit
    def test_empty_string(self) -> None:
        result = _parse_cookie_string("")
        assert result == {}


class TestBuildSession:
    @pytest.mark.unit
    def test_returns_session_with_cookies(self) -> None:
        session = build_session("foo=bar; baz=qux")
        assert session.cookies.get("foo") == "bar"
        assert session.cookies.get("baz") == "qux"

    @pytest.mark.unit
    def test_user_agent_set(self) -> None:
        session = build_session("x=y")
        assert "Mozilla" in session.headers.get("User-Agent", "")
