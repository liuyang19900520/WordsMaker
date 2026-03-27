"""Main pipeline: PDF → OCR → NLP → DynamoDB → Eudic import."""
import logging
from dataclasses import dataclass
from typing import List, Optional

from words_maker.config import Config
from words_maker.eudic.client import build_session
from words_maker.eudic.importer import FileEudicImporter, HttpEudicImporter
from words_maker.eudic.word_list import fetch_all_words
from words_maker.nlp.processor import process_text
from words_maker.ocr.pdf_extractor import extract_images_from_pdf
from words_maker.ocr.vision_client import detect_text
from words_maker.storage.dynamodb_repository import DynamoDBWordRepository, ensure_table_exists

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineResult:
    pages_processed: int
    words_extracted: int
    words_new_to_eudic: int
    words_imported: List[str]
    words_failed: List[str]
    fallback_file: Optional[str]  # set when FileEudicImporter was used


def run(config: Config, pdf_path: str, start_page: int, end_page: int) -> PipelineResult:
    """Execute the full pipeline.

    Steps:
        1. PDF → images (PyMuPDF)
        2. Images → text (Google Vision)
        3. Text → word frequencies (spaCy + NLTK)
        4. Upsert frequencies into DynamoDB
        5. Fetch existing Eudic words
        6. Diff → new words only
        7. Import new words into Eudic (HTTP API, with file fallback)
    """
    # --- Step 1: PDF → images ---
    logger.info("Extracting pages %d–%d from %s", start_page, end_page, pdf_path)
    images = extract_images_from_pdf(pdf_path, start_page, end_page)
    logger.info("Extracted %d page images", len(images))

    # --- Step 2: Images → text ---
    all_text_parts: List[str] = []
    for i, img_bytes in enumerate(images, start=start_page):
        logger.info("OCR page %d", i)
        text = detect_text(img_bytes, config.google_api_key)
        if text:
            all_text_parts.append(text)

    full_text = " ".join(all_text_parts)
    logger.info("OCR complete, total characters: %d", len(full_text))

    # --- Step 3: NLP ---
    logger.info("Running NLP processor")
    word_freq = process_text(full_text)
    logger.info("Extracted %d unique words", len(word_freq))

    # --- Step 4: DynamoDB ---
    logger.info("Upserting to DynamoDB")
    ensure_table_exists(config)
    repo = DynamoDBWordRepository(config)
    repo.upsert_frequencies(word_freq)

    # --- Step 5 & 6: Eudic diff ---
    logger.info("Fetching existing Eudic words")
    eudic_session = build_session(config.eudic_cookie)
    existing_words = fetch_all_words(eudic_session)

    new_words = sorted(w for w in word_freq if w not in existing_words)
    logger.info("New words not in Eudic: %d", len(new_words))

    # --- Step 7: Import ---
    fallback_file: str | None = None
    fallback_count = 0
    http_importer = HttpEudicImporter(eudic_session, config.eudic_default_category_id)
    succeeded, failed = http_importer.import_words(new_words)

    if failed:
        logger.warning(
            "%d words failed HTTP import, falling back to file export", len(failed)
        )
        file_importer = FileEudicImporter("Upload.txt")
        file_succeeded, _ = file_importer.import_words(failed)
        succeeded.extend(file_succeeded)
        fallback_count = len(file_succeeded)
        fallback_file = "Upload.txt"

    logger.info(
        "Pipeline complete: %d imported, %d via file fallback",
        len(succeeded),
        fallback_count,
    )

    return PipelineResult(
        pages_processed=len(images),
        words_extracted=len(word_freq),
        words_new_to_eudic=len(new_words),
        words_imported=succeeded,
        words_failed=[],
        fallback_file=fallback_file,
    )
