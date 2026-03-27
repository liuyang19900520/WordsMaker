"""Unit tests for nlp/processor.py – no network or AWS required."""
import pytest

from words_maker.nlp.processor import _get_wordnet_pos, _is_valid_english_word, process_text


class TestGetWordnetPos:
    def test_adjective(self) -> None:
        assert _get_wordnet_pos("JJ") == "a"

    def test_verb(self) -> None:
        assert _get_wordnet_pos("VB") == "v"

    def test_noun(self) -> None:
        assert _get_wordnet_pos("NN") == "n"

    def test_adverb(self) -> None:
        assert _get_wordnet_pos("RB") == "r"

    def test_default_is_noun(self) -> None:
        assert _get_wordnet_pos("XX") == "n"


class TestIsValidEnglishWord:
    @pytest.fixture(autouse=True)
    def word_set(self):
        return {"running", "cat", "dog", "beautiful"}

    def test_valid_word(self) -> None:
        assert _is_valid_english_word("cat", {"cat"})

    def test_single_letter_rejected(self) -> None:
        assert not _is_valid_english_word("a", {"a"})

    def test_digit_in_word_rejected(self) -> None:
        assert not _is_valid_english_word("word2", {"word2"})

    def test_not_in_word_set_rejected(self) -> None:
        assert not _is_valid_english_word("xyz123", {"cat"})

    def test_blank_rejected(self) -> None:
        assert not _is_valid_english_word("  ", set())


class TestProcessText:
    @pytest.mark.unit
    def test_returns_dict(self) -> None:
        result = process_text("The cat sat on the mat.")
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_stopwords_excluded(self) -> None:
        result = process_text("The the the")
        assert "the" not in result

    @pytest.mark.unit
    def test_lemmatization(self) -> None:
        result = process_text("running cats dogs")
        # 'running' → 'running' (verb) or 'run', 'cats' → 'cat'
        assert "cat" in result or "cats" not in result

    @pytest.mark.unit
    def test_single_letters_excluded(self) -> None:
        result = process_text("a b c dog")
        for letter in "abcdefghijklmnopqrstuvwxyz":
            assert letter not in result

    @pytest.mark.unit
    def test_empty_text(self) -> None:
        result = process_text("")
        assert result == {}
