import logging
import time
from typing import Set

import requests

logger = logging.getLogger(__name__)

_WORDS_URL = (
    "https://my.eudic.net/StudyList/WordsDataSource"
    "?=9"
    "&draw={draw}"
    "&columns%5B0%5D%5Bdata%5D=id"
    "&columns%5B0%5D%5Bsearchable%5D=false"
    "&columns%5B0%5D%5Borderable%5D=false"
    "&columns%5B1%5D%5Bdata%5D=id"
    "&columns%5B1%5D%5Bsearchable%5D=true"
    "&columns%5B2%5D%5Bdata%5D=word"
    "&columns%5B2%5D%5Borderable%5D=true"
    "&columns%5B3%5D%5Bdata%5D=phon"
    "&columns%5B3%5D%5Bsearchable%5D=true"
    "&columns%5B4%5D%5Bdata%5D=exp"
    "&columns%5B4%5D%5Bsearchable%5D=true"
    "&columns%5B5%5D%5Bdata%5D=rating"
    "&columns%5B5%5D%5Borderable%5D=true"
    "&columns%5B6%5D%5Bdata%5D=addtime"
    "&order%5B0%5D%5Bcolumn%5D=6"
    "&order%5B0%5D%5Bdir%5D=desc"
    "&start={start}"
    "&length={length}"
    "&search%5Bvalue%5D="
    "&categoryid={category}"
)

_PAGE_SIZE = 500
_REQUEST_DELAY = 1.0  # seconds between paginated requests


def fetch_all_words(session: requests.Session) -> Set[str]:
    """Fetch every word in the Eudic study list (all categories).

    Args:
        session: Authenticated requests session (from eudic.client.build_session).

    Returns:
        Set of all word strings currently in the user's Eudic study list.
    """
    # category -1 = all words
    url = _WORDS_URL.format(draw=1, start=0, length=1, category=-1)
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    try:
        total = resp.json()["recordsTotal"]
    except Exception:
        logger.warning(
            "Eudic API returned non-JSON (cookie expired or invalid?). "
            "Treating existing word list as empty."
        )
        return set()
    logger.info("Eudic total words: %d", total)

    all_words: Set[str] = set()
    draw = 2
    start = 0

    while start < total:
        url = _WORDS_URL.format(draw=draw, start=start, length=_PAGE_SIZE, category=-1)
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        for item in data:
            word = item.get("uuid") or item.get("word", "")
            if word:
                all_words.add(word.strip().lower())
        start += _PAGE_SIZE
        draw += 1
        if start < total:
            time.sleep(_REQUEST_DELAY)

    logger.info("Fetched %d existing Eudic words", len(all_words))
    return all_words
