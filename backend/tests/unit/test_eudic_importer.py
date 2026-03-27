"""Unit tests for eudic/importer.py."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests

from words_maker.eudic.importer import FileEudicImporter, HttpEudicImporter


class TestFileEudicImporter:
    @pytest.mark.unit
    def test_writes_words_to_file(self, tmp_path: Path) -> None:
        output = tmp_path / "Upload.txt"
        importer = FileEudicImporter(str(output))
        succeeded, failed = importer.import_words(["apple", "banana", "cherry"])
        assert failed == []
        assert set(succeeded) == {"apple", "banana", "cherry"}
        lines = output.read_text(encoding="utf-8").strip().splitlines()
        assert lines == ["apple", "banana", "cherry"]

    @pytest.mark.unit
    def test_empty_list(self, tmp_path: Path) -> None:
        output = tmp_path / "Upload.txt"
        importer = FileEudicImporter(str(output))
        succeeded, failed = importer.import_words([])
        assert succeeded == []
        assert failed == []


class TestHttpEudicImporter:
    def _make_session(self, response_json: dict, status_code: int = 200) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = response_json
        mock_resp.raise_for_status = MagicMock()

        mock_session = MagicMock(spec=requests.Session)
        mock_session.post.return_value = mock_resp
        mock_session.headers = {}
        return mock_session

    @pytest.mark.unit
    def test_import_words_success(self) -> None:
        session = self._make_session({"msg": "单词导入成功,导入数量：3"})
        importer = HttpEudicImporter(session, "0")
        succeeded, failed = importer.import_words(["apple", "banana", "cherry"])
        assert set(succeeded) == {"apple", "banana", "cherry"}
        assert failed == []

    @pytest.mark.unit
    def test_import_words_api_failure(self) -> None:
        session = self._make_session({"msg": "error"})
        importer = HttpEudicImporter(session, "0")
        succeeded, failed = importer.import_words(["apple", "banana"])
        assert succeeded == []
        assert set(failed) == {"apple", "banana"}

    @pytest.mark.unit
    def test_import_words_empty(self) -> None:
        session = self._make_session({})
        importer = HttpEudicImporter(session, "0")
        succeeded, failed = importer.import_words([])
        assert succeeded == []
        assert failed == []

    @pytest.mark.unit
    def test_import_words_connection_error(self) -> None:
        mock_session = MagicMock(spec=requests.Session)
        mock_session.post.side_effect = requests.exceptions.ConnectionError("timeout")
        mock_session.headers = {}
        importer = HttpEudicImporter(mock_session, "0")
        succeeded, failed = importer.import_words(["apple", "banana"])
        assert succeeded == []
        assert set(failed) == {"apple", "banana"}

    @pytest.mark.unit
    def test_batch_sends_all_words_in_one_request(self) -> None:
        session = self._make_session({"msg": "单词导入成功,导入数量：2"})
        importer = HttpEudicImporter(session, "0")
        importer.import_words(["alpha", "beta"])
        assert session.post.call_count == 1
        call_data = session.post.call_args[1]["data"]
        assert "alpha\nbeta" == call_data["sentenceText"]
