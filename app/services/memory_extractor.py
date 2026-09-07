import re
from typing import List


class MemoryExtractor:

    # =====================================================
    # EXTRACT MEMORIES
    # =====================================================

    def extract(
        self,
        message: str,
    ) -> List[str]:

        message = message.strip()

        if not message:
            return []

        memories = []

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        name_match = re.search(
            r"\b(?:my name is|call me)\s+"
            r"([A-Za-z][A-Za-z\s'-]{1,40})",
            message,
            re.IGNORECASE,
        )

        if name_match:

            name = self._clean_value(
                name_match.group(1)
            )

            if name:
                memories.append(
                    f"User's name is {name}."
                )

        # -------------------------------------------------
        # LIKES
        # -------------------------------------------------

        like_match = re.search(
            r"\b(?:i like|i love|i enjoy)\s+"
            r"(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )

        if like_match:

            thing = self._clean_value(
                like_match.group(1)
            )

            if thing:
                memories.append(
                    f"User likes {thing}."
                )

        # -------------------------------------------------
        # DISLIKES
        # -------------------------------------------------

        dislike_match = re.search(
            r"\b(?:i dislike|i hate|i don't like|i do not like)\s+"
            r"(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )

        if dislike_match:

            thing = self._clean_value(
                dislike_match.group(1)
            )

            if thing:
                memories.append(
                    f"User dislikes {thing}."
                )

        # -------------------------------------------------
        # PROFESSION / ROLE
        # -------------------------------------------------

        role_match = re.search(
            r"\b(?:i am a|i'm a|i work as a|i work as an)\s+"
            r"(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )

        if role_match:

            role = self._clean_value(
                role_match.group(1)
            )

            if role:
                memories.append(
                    f"User works as {role}."
                )

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        location_match = re.search(
            r"\b(?:i live in|i'm from|i am from)\s+"
            r"(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )

        if location_match:

            location = self._clean_value(
                location_match.group(1)
            )

            if location:
                memories.append(
                    f"User lives in {location}."
                )

        # -------------------------------------------------
        # FAVORITE
        # -------------------------------------------------

        favorite_match = re.search(
            r"\bmy favou?rite\s+"
            r"(.+?)\s+is\s+(.+?)(?:[.!?]|$)",
            message,
            re.IGNORECASE,
        )

        if favorite_match:

            category = self._clean_value(
                favorite_match.group(1)
            )

            value = self._clean_value(
                favorite_match.group(2)
            )

            if category and value:
                memories.append(
                    f"User's favorite {category} is {value}."
                )

        return memories

    # =====================================================
    # CLEAN EXTRACTED VALUE
    # =====================================================

    def _clean_value(
        self,
        value: str,
    ) -> str:

        value = value.strip()

        # Remove unnecessary trailing punctuation.
        value = value.rstrip(".,!?")

        # Remove accidental whitespace.
        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value


# =========================================================
# SINGLE SERVICE INSTANCE
# =========================================================

memory_extractor = MemoryExtractor()