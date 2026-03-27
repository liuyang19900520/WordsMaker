"""AWS Lambda entry points.

Two handlers:

1. handler(event, context)
   - S3 event: PDF uploaded → full pipeline (OCR → NLP → DynamoDB → Eudic import)
   - HTTP (API Gateway): POST {"pdf_key": "...", "pages": "1-15"}

2. sync_handler(event, context)
   - EventBridge scheduled rule (daily cron) → incremental Eudic → DynamoDB sync
   - Also callable manually via Lambda console or CLI

Environment variables:
  GOOGLE_API_KEY, EUDIC_COOKIE, DYNAMODB_TABLE_NAME, AWS_REGION, S3_BUCKET
  See .env.example for the full list.
"""
import json
import logging
import os
import tempfile

import boto3

from words_maker.config import load_config
from words_maker.eudic.client import build_session
from words_maker.eudic.sync import run_sync
from words_maker.pipeline import run

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context: object) -> dict:
    """PDF pipeline handler (S3 trigger or HTTP)."""
    config = load_config()
    start_page: int = config.pdf_start_page
    end_page: int = config.pdf_end_page

    if "Records" in event:
        # S3 trigger
        record = event["Records"][0]
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        logger.info("S3 trigger: s3://%s/%s", bucket, key)
        s3 = boto3.client("s3", region_name=config.aws_region)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            s3.download_fileobj(bucket, key, tmp)
            pdf_local_path = tmp.name

    else:
        # HTTP / direct invocation
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
        pdf_key = body.get("pdf_key")
        if not pdf_key:
            return {"statusCode": 400, "body": json.dumps({"error": "pdf_key is required"})}
        pages_str = body.get("pages", f"{start_page}-{end_page}")
        parts = pages_str.split("-")
        start_page = int(parts[0])
        end_page = int(parts[1]) if len(parts) > 1 else int(parts[0])
        bucket = os.environ.get("S3_BUCKET", "")
        if not bucket:
            return {"statusCode": 500, "body": json.dumps({"error": "S3_BUCKET not configured"})}
        s3 = boto3.client("s3", region_name=config.aws_region)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            s3.download_fileobj(bucket, pdf_key, tmp)
            pdf_local_path = tmp.name

    result = run(config, pdf_local_path, start_page, end_page)
    return {
        "statusCode": 200,
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
        "body": json.dumps({
            "new_words": result.new_words,
            "pages_fetched": result.pages_fetched,
            "checkpoint_before": result.checkpoint_before,
            "checkpoint_after": result.checkpoint_after,
        }),
    }
