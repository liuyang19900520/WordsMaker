from typing import Dict, Protocol


class WordRepository(Protocol):
    """Storage interface for word frequency data."""

    def upsert_frequencies(self, word_freq: Dict[str, int]) -> None:
        """Add frequencies to existing records (atomic ADD per word).

        Creates a new record with first_seen/last_seen timestamps if
        the word does not exist yet; otherwise increments freq and
        updates last_seen.

        Args:
            word_freq: Mapping of word (lowercase lemma) → frequency delta.
        """
        ...
