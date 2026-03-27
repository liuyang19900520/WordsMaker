"""Local development server — mirrors the Lambda Function URL interface.

Usage:
    cd backend
    cp .env.example .env.local   # fill in your credentials
    python local_server.py

Then set in frontend/.env.local:
    LAMBDA_FUNCTION_URL=http://localhost:8001
"""
import logging
import os
import sys
import tempfile

from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Load .env.local (falls back to .env.example values if not present)
load_dotenv(".env.local")
load_dotenv(".env.example")

# Make the src package importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from words_maker.config import load_config  # noqa: E402
from words_maker.pipeline import run  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB


@app.post("/")
def process_pdf():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "file is required"}), 400

    eudic_cookie = request.form.get("eudic_cookie", "").strip()
    if not eudic_cookie:
        return jsonify({"error": "eudic_cookie is required"}), 400

    start_page = int(request.form.get("start_page", "1"))
    end_page = int(request.form.get("end_page", "15"))

    # Override EUDIC_COOKIE with the one sent from the frontend
    os.environ["EUDIC_COOKIE"] = eudic_cookie

    config = load_config()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        file.save(tmp)
        pdf_path = tmp.name

    try:
        result = run(config, pdf_path, start_page, end_page)
    finally:
        os.unlink(pdf_path)

    return jsonify({
        "pages_processed": result.pages_processed,
        "words_extracted": result.words_extracted,
        "words_new_to_eudic": result.words_new_to_eudic,
        "words_imported": len(result.words_imported),
        "words_imported_list": result.words_imported,
        "fallback_file": result.fallback_file,
    })


if __name__ == "__main__":
    port = int(os.environ.get("LOCAL_SERVER_PORT", "8001"))
    logger.info("Local server running at http://localhost:%d", port)
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
