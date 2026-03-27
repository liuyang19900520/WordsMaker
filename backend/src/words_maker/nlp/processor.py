import logging
import string
from typing import Dict, Set

import nltk
import spacy
from nltk.corpus import stopwords, words as nltk_words
from nltk.corpus.reader.wordnet import ADJ, ADV, NOUN, VERB
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

_PUNCTUATION: Set[str] = set(string.punctuation)
_SINGLE_LETTERS: Set[str] = set(string.ascii_lowercase)


def _ensure_nltk_data() -> None:
    for resource in ("punkt_tab", "stopwords", "averaged_perceptron_tagger_eng", "wordnet", "words"):
        nltk.download(resource, quiet=True)


def _get_wordnet_pos(tag: str) -> str:
    if tag.startswith("J"):
        return ADJ
    if tag.startswith("V"):
        return VERB
    if tag.startswith("N"):
        return NOUN
    if tag.startswith("R"):
        return ADV
    return NOUN


def _is_valid_english_word(word: str, word_set: Set[str]) -> bool:
    return (
        word.lower() in word_set
        and word not in _SINGLE_LETTERS
        and not any(ch.isdigit() for ch in word)
        and word.strip() != ""
    )


def process_text(text: str) -> Dict[str, int]:
    """Tokenize, lemmatize, filter, and count word frequencies.

    Uses spaCy for NER (to remove person names) and NLTK for
    POS-tagged lemmatization and stopword removal.

    Args:
        text: Raw text extracted from OCR.

    Returns:
        Mapping of lemma → frequency (only valid English words,
        excluding stopwords, punctuation, digits, and person names).
    """
    _ensure_nltk_data()

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    person_names: Set[str] = {ent.text.lower() for ent in doc.ents if ent.label_ == "PERSON"}

    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)

    lemmatizer = WordNetLemmatizer()
    lemmas = [
        lemmatizer.lemmatize(token.lower(), _get_wordnet_pos(pos))
        for token, pos in pos_tags
    ]

    stop_words = set(stopwords.words("english"))
    word_set = set(nltk_words.words())

    freq: Dict[str, int] = {}
    for lemma in lemmas:
        if (
            lemma in stop_words
            or lemma in _PUNCTUATION
            or lemma in person_names
            or not _is_valid_english_word(lemma, word_set)
        ):
            continue
        freq[lemma] = freq.get(lemma, 0) + 1

    return freq
