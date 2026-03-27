import base64
import json
import logging

import requests

logger = logging.getLogger(__name__)

_VISION_URL = "https://vision.googleapis.com/v1/images:annotate?key={api_key}"


def detect_text(image_bytes: bytes, api_key: str) -> str:
    """Call Google Vision API to extract text from an image.

    Args:
        image_bytes: Raw image bytes (PNG or JPEG).
        api_key: Google Cloud Vision API key.

    Returns:
        Extracted text as a single string, or empty string on failure.
    """
    url = _VISION_URL.format(api_key=api_key)
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "requests": [
            {
                "image": {"content": encoded_image},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()

    if "error" in result:
        logger.error("Vision API error: %s", result["error"].get("message"))
        return ""

    responses = result.get("responses", [])
    if not responses:
        return ""

    annotations = responses[0].get("textAnnotations", [])
    if not annotations:
        return ""

    # First annotation contains the full-page text
    return annotations[0].get("description", "")
