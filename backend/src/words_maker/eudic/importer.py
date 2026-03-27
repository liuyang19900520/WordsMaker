"""Eudic word importer.

Two strategies:
1. HttpEudicImporter  – POST /StudyList/ImportText (confirmed endpoint)
2. FileEudicImporter  – write Upload.txt fallback

Confirmed payload format (from DevTools capture):
    sentenceText=word1\nword2\nword3&categoryid=0&cateNameInput=&isSingleWords=true
"""
import logging
from pathlib import Path
from typing import List, Tuple

import requests

logger = logging.getLogger(__name__)

_IMPORT_URL = "https://my.eudic.net/StudyList/ImportText"
_EDIT_URL = "https://my.eudic.net/StudyList/Edit"


class HttpEudicImporter:
    """Import words via the confirmed Eudic /StudyList/ImportText API.

    Sends all words in a single batch request (newline-separated).
    """

    def __init__(self, session: requests.Session, category_id: str = "0") -> None:
        self._session = session
        self._category_id = category_id
        self._session.headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://my.eudic.net/studylist/import/",
            }
        )

    def import_words(self, words: List[str]) -> Tuple[List[str], List[str]]:
        """Import all words in a single batch request.

        Returns (succeeded, failed). On any error the entire batch is
        treated as failed so the caller can fall back to FileEudicImporter.
        """
        if not words:
            return [], []

        sentence_text = "\n".join(words)
        data = {
            "sentenceText": sentence_text,
            "categoryid": self._category_id,
            "cateNameInput": "",
            "isSingleWords": "true",
        }
        try:
            resp = self._session.post(_IMPORT_URL, data=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            logger.debug("ImportText response: %s", result)
            # Eudic returns {"msg": "单词导入成功,导入数量：N"} on success
            msg = result.get("msg", "")
            if "导入成功" in msg or "成功" in msg:
                logger.info("Imported %d words via Eudic API: %s", len(words), msg)
                return list(words), []
            logger.warning("ImportText returned unexpected response: %s", result)
            return [], list(words)
        except Exception as exc:
            logger.warning("ImportText batch failed: %s", exc)
            return [], list(words)

    def change_rating(self, word: str, rating: int) -> bool:
        """Change the star rating of a word already in the study list."""
        data = {
            "oper": "changerating",
            "uuid": word,
            "newrating": str(rating),
            "oldcateid": "-1",
        }
        try:
            resp = self._session.post(_EDIT_URL, data=data, timeout=10)
            resp.raise_for_status()
            return resp.json().get("result") is True
        except Exception as exc:
            logger.warning("change_rating failed for '%s': %s", word, exc)
            return False


class FileEudicImporter:
    """Fallback: write an Upload.txt file for manual import into Eudic."""

    def __init__(self, output_path: str = "Upload.txt") -> None:
        self._output_path = Path(output_path)

    def import_words(self, words: List[str]) -> Tuple[List[str], List[str]]:
        """Write words to a text file; all words are 'succeeded'."""
        self._output_path.write_text("\n".join(words) + "\n", encoding="utf-8")
        logger.info("Wrote %d words to %s", len(words), self._output_path)
        return list(words), []
