"""AWS Lambda entry points.

Two handlers:

1. handler(event, context)
   - HTTP (Function URL): POST multipart/form-data
       fields: file (PDF), start_page, end_page, eudic_cookie

2. sync_handler(event, context)
   - EventBridge scheduled rule (daily cron) → incremental Eudic → DynamoDB sync
   - Also callable manually via Lambda console or CLI

Environment variables:
  GOOGLE_API_KEY, DYNAMODB_TABLE_NAME, AWS_REGION
  See .env.example for the full list.
"""
import base64
import email
import json
import logging
import tempfile
from email.policy import HTTP

from words_maker.config import load_config
from words_maker.eudic.client import build_session
from words_maker.eudic.sync import run_sync
from words_maker.pipeline import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _parse_multipart(event: dict) -> dict:
    """Parse multipart/form-data from a Lambda Function URL event.

    Returns a dict with keys: file_bytes, start_page, end_page, eudic_cookie.
    """
    content_type = ""
    for k, v in (event.get("headers") or {}).items():
        if k.lower() == "content-type":
            content_type = v
            break

    body = event.get("body", "")
    if event.get("isBase64Encoded"):
        body_bytes = base64.b64decode(body)
    else:
        body_bytes = body.encode("utf-8") if isinstance(body, str) else body

    # Use email library to parse multipart
    raw = f"Content-Type: {content_type}\r\n\r\n".encode() + body_bytes
    msg = email.message_from_bytes(raw, policy=HTTP)

    fields: dict = {}
    for part in msg.walk():
        cd = part.get("Content-Disposition", "")
        if not cd:
            continue
        name = None
        for segment in cd.split(";"):
            segment = segment.strip()
            if segment.startswith('name='):
                name = segment[5:].strip('"')
        if name is None:
            continue
        payload = part.get_payload(decode=True)
        if name == "file":
            fields["file_bytes"] = payload
        else:
            fields[name] = payload.decode("utf-8") if payload else ""

    return fields


def handler(event: dict, context: object) -> dict:
    """PDF pipeline handler — accepts multipart/form-data via Function URL."""
    logger.info("Event keys: %s", list(event.keys()))

    try:
        fields = _parse_multipart(event)
    except Exception as exc:
        logger.exception("Failed to parse multipart body")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Failed to parse request: {exc}"}),
        }

    file_bytes = fields.get("file_bytes")
    if not file_bytes:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing PDF file"}),
        }

    eudic_cookie = fields.get("eudic_cookie", "")
    if not eudic_cookie:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing eudic_cookie"}),
        }

    config = load_config(eudic_cookie=eudic_cookie)

    try:
        start_page = int(fields.get("start_page", config.pdf_start_page))
        end_page = int(fields.get("end_page", config.pdf_end_page))
    except ValueError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "start_page / end_page must be integers"}),
        }

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        pdf_path = tmp.name

    logger.info("Processing %d bytes, pages %d-%d", len(file_bytes), start_page, end_page)
    result = run(config, pdf_path, start_page, end_page)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "pages_processed": result.pages_processed,
            "words_extracted": result.words_extracted,
            "words_new_to_eudic": result.words_new_to_eudic,
            "words_imported": len(result.words_imported),
            "words_imported_list": result.words_imported,
            "fallback_file": result.fallback_file,
        }),
    }


def sync_handler(event: dict, context: object) -> dict:
    """Daily incremental sync: Eudic → DynamoDB.

    Triggered by EventBridge schedule:
        cron(0 2 * * ? *)   # every day at 02:00 UTC
    """
    logger.info("Starting daily Eudic sync")
    config = load_config()
    session = build_session(config.eudic_cookie)
    result = run_sync(config, session)

    logger.info(
        "Sync complete: %d new words, %d pages fetched, checkpoint %s → %s",
        result.new_words,
        result.pages_fetched,
        result.checkpoint_before,
        result.checkpoint_after,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "new_words": result.new_words,
            "pages_fetched": result.pages_fetched,
            "checkpoint_before": result.checkpoint_before,
            "checkpoint_after": result.checkpoint_after,
        }),
    }
