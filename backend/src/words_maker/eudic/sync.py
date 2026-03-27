"""Incremental sync: Eudic → DynamoDB.

Algorithm:
1. Read _sync_checkpoint from DynamoDB (last sync time, ISO 8601)
2. Fetch Eudic words sorted by addtime DESC
3. Stop paginating once addtime <= checkpoint
4. Write new words with freq = f(rating)
5. Save new checkpoint = now

The _sync_checkpoint item uses word="_sync_checkpoint" as its PK.
If checkpoint is missing, falls back to full sync.

Rating → freq:
  5★ → 15, 4★ → 8, 3★ → 4, 2★ → 2, 1★ → 1, 0★ → 1
"""
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import boto3
import requests

from words_maker.config import Config

logger = logging.getLogger(__name__)

_CHECKPOINT_KEY = "_sync_checkpoint"
_CHECKPOINT_FIELD = "last_sync_time"

_RATING_TO_FREQ: Dict[int, int] = {5: 15, 4: 8, 3: 4, 2: 2, 1: 1, 0: 1}

_URL_TEMPLATE = (
    "https://my.eudic.net/StudyList/WordsDataSource"
    "?=9&draw={draw}"
    "&columns%5B2%5D%5Bdata%5D=word&columns%5B2%5D%5Borderable%5D=true"
    "&columns%5B5%5D%5Bdata%5D=rating&columns%5B5%5D%5Borderable%5D=true"
    "&columns%5B6%5D%5Bdata%5D=addtime"
    "&order%5B0%5D%5Bcolumn%5D=6&order%5B0%5D%5Bdir%5D=desc"
    "&start={start}&length={length}"
    "&search%5Bvalue%5D=&search%5Bregex%5D=false"
    "&categoryid=-1"
)

PAGE_SIZE = 100
REQUEST_DELAY = 0.5


@dataclass(frozen=True)
class SyncResult:
    new_words: int
    checkpoint_before: Optional[str]
    checkpoint_after: str
    pages_fetched: int


def _get_table(config: Config):
    kwargs: Dict = {"region_name": config.aws_region}
    if config.aws_access_key_id:
        kwargs["aws_access_key_id"] = config.aws_access_key_id
        kwargs["aws_secret_access_key"] = config.aws_secret_access_key
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(config.dynamodb_table_name)


def _load_checkpoint(table) -> Optional[str]:
    resp = table.get_item(Key={"word": _CHECKPOINT_KEY})
    item = resp.get("Item")
    if not item:
        return None
    return item.get(_CHECKPOINT_FIELD)


def _save_checkpoint(table, timestamp: str) -> None:
    table.put_item(Item={"word": _CHECKPOINT_KEY, _CHECKPOINT_FIELD: timestamp})
    logger.info("Checkpoint saved: %s", timestamp)


def _fetch_new_words(
    session: requests.Session, checkpoint: Optional[str]
) -> Tuple[List[Dict], int]:
    """Fetch words added after checkpoint (or all if checkpoint is None).

    Returns (list of {word, freq}, pages_fetched).
    """
    new_words: List[Dict] = []
    pages_fetched = 0
    draw = 1

    # Get total so we know when to stop even if all pages are new
    url = _URL_TEMPLATE.format(draw=draw, start=0, length=1)
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    total = resp.json()["recordsTotal"]
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    logger.info("Eudic total: %d words, checkpoint: %s", total, checkpoint or "none (full sync)")

    for page in range(total_pages):
        start = page * PAGE_SIZE
        draw = page + 2
        url = _URL_TEMPLATE.format(draw=draw, start=start, length=PAGE_SIZE)
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        pages_fetched += 1

        data = resp.json().get("data", [])
        stop = False

        for item in data:
            word = (item.get("uuid") or item.get("word", "")).strip().lower()
            rating = int(item.get("rating") or 0)
            addtime = item.get("addtime", "")

            if not word or word.startswith("_"):
                continue

            # addtime is ISO string; string comparison works for ISO 8601
            if checkpoint and addtime <= checkpoint:
                stop = True
                break

            new_words.append({
                "word": word,
                "freq": _RATING_TO_FREQ.get(rating, 1),
            })

        if stop:
            logger.info("Reached checkpoint at page %d, stopping", page + 1)
            break

        if page < total_pages - 1:
            time.sleep(REQUEST_DELAY)

    return new_words, pages_fetched


def _write_words(table, words: List[Dict], now: str) -> int:
    """Upsert words into DynamoDB. Returns count of successful writes."""
    success = 0
    for item in words:
        try:
            table.update_item(
                Key={"word": item["word"]},
                UpdateExpression=(
                    "ADD freq :delta "
                    "SET first_seen = if_not_exists(first_seen, :ts), last_seen = :ts"
                ),
                ExpressionAttributeValues={
                    ":delta": item["freq"],
                    ":ts": now,
                },
            )
            success += 1
        except Exception as exc:
            logger.error("Failed to write '%s': %s", item["word"], exc)
    return success


def run_sync(config: Config, session: requests.Session) -> SyncResult:
    """Run incremental sync and return a result summary."""
    table = _get_table(config)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000")

    checkpoint = _load_checkpoint(table)
    new_words, pages_fetched = _fetch_new_words(session, checkpoint)

    if new_words:
        written = _write_words(table, new_words, now)
        logger.info("Wrote %d new words to DynamoDB", written)
    else:
        logger.info("No new words since last sync")

    _save_checkpoint(table, now)

    return SyncResult(
        new_words=len(new_words),
        checkpoint_before=checkpoint,
        checkpoint_after=now,
        pages_fetched=pages_fetched,
    )
