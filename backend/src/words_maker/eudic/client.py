import logging
from typing import Dict

import requests

logger = logging.getLogger(__name__)

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/129.0.0.0 Safari/537.36"
)


def _parse_cookie_string(cookie_string: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for part in cookie_string.split("; "):
        if "=" in part:
            key, _, value = part.partition("=")
            result[key] = value
    return result


def build_session(cookie_string: str) -> requests.Session:
    """Create an authenticated requests.Session for Eudic.

    Args:
        cookie_string: Raw Cookie header string copied from browser DevTools.

    Returns:
        Configured session with cookies and User-Agent set.
    """
    session = requests.Session()
    session.cookies.update(_parse_cookie_string(cookie_string))
    session.headers.update({"User-Agent": _USER_AGENT})
    return session
