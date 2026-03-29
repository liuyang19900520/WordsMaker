import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    google_api_key: str
    dynamodb_table_name: str
    aws_region: str
    eudic_cookie: str
    eudic_default_category_id: str
    pdf_start_page: int
    pdf_end_page: int
    aws_access_key_id: Optional[str]
    aws_secret_access_key: Optional[str]


def load_config(eudic_cookie: Optional[str] = None) -> Config:
    return Config(
        google_api_key=os.environ["GOOGLE_API_KEY"],
        dynamodb_table_name=os.environ.get("DYNAMODB_TABLE_NAME", "words_maker"),
        aws_region=os.environ.get("AWS_REGION", "ap-northeast-1"),
        eudic_cookie=eudic_cookie or os.environ.get("EUDIC_COOKIE", ""),
        eudic_default_category_id=os.environ.get("EUDIC_DEFAULT_CATEGORY_ID", "0"),
        pdf_start_page=int(os.environ.get("PDF_START_PAGE", "1")),
        pdf_end_page=int(os.environ.get("PDF_END_PAGE", "15")),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID") or None,
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY") or None,
    )
