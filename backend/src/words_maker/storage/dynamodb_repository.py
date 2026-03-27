import logging
from datetime import datetime, timezone
from typing import Dict, Optional

import boto3
from boto3.dynamodb.conditions import Attr  # noqa: F401 (Protocol satisfaction)

from words_maker.config import Config

logger = logging.getLogger(__name__)

_TABLE_KEY_SCHEMA = [{"AttributeName": "word", "KeyType": "HASH"}]
_TABLE_ATTRIBUTE_DEFS = [{"AttributeName": "word", "AttributeType": "S"}]


def _get_table(config: Config):
    kwargs: Dict = {"region_name": config.aws_region}
    if config.aws_access_key_id:
        kwargs["aws_access_key_id"] = config.aws_access_key_id
        kwargs["aws_secret_access_key"] = config.aws_secret_access_key
    dynamodb = boto3.resource("dynamodb", **kwargs)
    return dynamodb.Table(config.dynamodb_table_name)


def ensure_table_exists(config: Config) -> None:
    """Create the DynamoDB table if it does not already exist."""
    kwargs: Dict = {"region_name": config.aws_region}
    if config.aws_access_key_id:
        kwargs["aws_access_key_id"] = config.aws_access_key_id
        kwargs["aws_secret_access_key"] = config.aws_secret_access_key

    client = boto3.client("dynamodb", **kwargs)
    existing = [t for t in client.list_tables()["TableNames"] if t == config.dynamodb_table_name]
    if existing:
        return

    client.create_table(
        TableName=config.dynamodb_table_name,
        KeySchema=_TABLE_KEY_SCHEMA,
        AttributeDefinitions=_TABLE_ATTRIBUTE_DEFS,
        BillingMode="PAY_PER_REQUEST",
    )
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=config.dynamodb_table_name)
    logger.info("Created DynamoDB table: %s", config.dynamodb_table_name)


class DynamoDBWordRepository:
    """DynamoDB-backed implementation of WordRepository."""

    def __init__(self, config: Config) -> None:
        self._table = _get_table(config)

    def upsert_frequencies(self, word_freq: Dict[str, int]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._table.batch_writer() as _:
            pass  # batch_writer used for reads; updates must be individual

        for word, delta in word_freq.items():
            self._table.update_item(
                Key={"word": word},
                UpdateExpression=(
                    "ADD freq :delta "
                    "SET first_seen = if_not_exists(first_seen, :ts), last_seen = :ts"
                ),
                ExpressionAttributeValues={
                    ":delta": delta,
                    ":ts": now,
                },
            )
        logger.info("Upserted %d words into DynamoDB", len(word_freq))
