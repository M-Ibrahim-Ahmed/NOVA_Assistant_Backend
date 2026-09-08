import re
from typing import List


class MemoryRetriever:

    # =====================================================
    # MEMORY CATEGORIES
    # =====================================================

    CATEGORY_KEYWORDS = {

        "name": {
            "name",
            "called",
            "nickname",
        },

        "preference": {
            "like",
            "likes",
            "love",
            "loves",
            "enjoy",
            "enjoys",
            "favorite",
            "favourite",
            "prefer",
            "preference",
        },

        "work": {
            "work",
            "works",
            "job",
            "profession",
            "career",
            "developer",
            "engineer",
            "occupation",
        },

        "location": {
            "live",
            "lives",
            "from",
            "location",
            "city",
            "country",
            "home",
        },

        "programming": {
            "programming",
            "language",
            "code",
            "coding",
            "python",
            "javascript",
            "java",
            "dart",
            "flutter",
        },
    }

    # =====================================================
    # RETRIEVE RELEVANT MEMORIES
    # =====================================================

    def retrieve(
        self,
        message: str,
        memories: List[str],
        max_results: int = 5,
    ) -> List[str]:

        if not message.strip():
            return []

        if not memories:
            return []

        message_words = self._tokenize(message)

        if not message_words:
            return []

        # -------------------------------------------------
        # DETERMINE USER INTENT
        # -------------------------------------------------

        detected_categories = (
            self._detect_categories(
                message_words
            )
        )

        scored_memories = []

        # -------------------------------------------------
        # SCORE MEMORIES
        # -------------------------------------------------

        for memory in memories:

            memory_words = self._tokenize(
                memory
            )

            if not memory_words:
                continue

            memory_categories = (
                self._detect_categories(
                    memory_words
                )
            )

            score = 0

            # ---------------------------------------------
            # CATEGORY MATCH
            # ---------------------------------------------

            matching_categories = (
                detected_categories
                .intersection(memory_categories)
            )

            if matching_categories:

                score += (
                    len(matching_categories) * 10
                )

            # ---------------------------------------------
            # WORD OVERLAP
            # ---------------------------------------------

            overlap = (
                message_words
                .intersection(memory_words)
            )

            score += len(overlap)

            # ---------------------------------------------
            # ONLY KEEP RELEVANT MEMORIES
            # ---------------------------------------------

            if score > 0:

                scored_memories.append(
                    (
                        score,
                        memory,
                    )
                )

        # -------------------------------------------------
        # SORT BY SCORE
        # -------------------------------------------------

        scored_memories.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # -------------------------------------------------
        # CATEGORY FILTER
        #
        # If we detected a clear category, only return
        # memories belonging to that category.
        # -------------------------------------------------

        if detected_categories:

            category_results = []

            for score, memory in scored_memories:

                memory_categories = (
                    self._detect_categories(
                        self._tokenize(memory)
                    )
                )

                if memory_categories.intersection(
                    detected_categories
                ):

                    category_results.append(
                        memory
                    )

            if category_results:

                return category_results[
                    :max_results
                ]

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        return [
            memory
            for _, memory
            in scored_memories[:max_results]
        ]

    # =====================================================
    # DETECT CATEGORIES
    # =====================================================

    def _detect_categories(
        self,
        words: set[str],
    ) -> set[str]:

        categories = set()

        # -------------------------------------------------
        # SPECIFIC INTENTS
        # -------------------------------------------------

        specific_categories = {
            "name",
            "work",
            "location",
            "programming",
        }

        for category in specific_categories:

            keywords = self.CATEGORY_KEYWORDS[category]

            if words.intersection(keywords):

                categories.add(category)

        # -------------------------------------------------
        # PREFERENCE
        #
        # Only use generic preference when there is no
        # more specific intent.
        # -------------------------------------------------

        if not categories:

            preference_keywords = (
                self.CATEGORY_KEYWORDS["preference"]
            )

            if words.intersection(
                preference_keywords
            ):

                categories.add("preference")

        return categories

    # =====================================================
    # TOKENIZE
    # =====================================================

    def _tokenize(
        self,
        text: str,
    ) -> set[str]:

        words = re.findall(
            r"\b[a-zA-Z]{2,}\b",
            text.lower(),
        )

        stop_words = {
            "the",
            "and",
            "that",
            "this",
            "with",
            "from",
            "have",
            "has",
            "was",
            "were",
            "are",
            "you",
            "your",
            "what",
            "when",
            "where",
            "which",
            "who",
            "how",
            "why",
            "does",
            "did",
            "can",
            "could",
            "would",
            "should",
            "tell",
            "about",
            "for",
            "please",
            "my",
            "me",
            "i",
            "do",
            "is",
            "it",
        }

        return {
            word
            for word in words
            if word not in stop_words
        }


# =========================================================
# SINGLE SERVICE INSTANCE
# =========================================================

memory_retriever = MemoryRetriever()