import re
from typing import List


class MemoryExtractor:

    def extract(
        self,
        message: str,
    ) -> List[str]:

        message = message.strip()

        if not message:
            return []

        memories = []

        # =================================================
        # NAME
        # =================================================

        name_match = re.search(
            r"\b(?:my name is|call me)\s+"
            r"([A-Za-z][A-Za-z\s'-]{1,40}?)"
            r"(?:[.!?,]|$)",
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

        # =================================================
        # LIKES
        # =================================================

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

        # =================================================
        # DISLIKES
        # =================================================

        dislike_match = re.search(
            r"\b(?:i dislike|i hate|i don't like|"
            r"i do not like)\s+"
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

        # =================================================
        # PROFESSION / ROLE
        # =================================================

        role_match = re.search(
            r"\b(?:i am a|i'm a|i work as a|"
            r"i work as an|i work as)\s+"
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

        # =================================================
        # LOCATION
        # =================================================
        #
        # Examples:
        #
        # I live in Islamabad.
        # I moved to Lahore.
        # I've moved to Dubai.
        # I have moved to Karachi.
        # I'm from Taxila.
        #
        # The non-greedy capture prevents extra words
        # from being accidentally included.
        # =================================================

        location_match = re.search(
            r"\b(?:i live in|i'm from|i am from|"
            r"i moved to|i've moved to|"
            r"i have moved to)\s+"
            r"([A-Za-z][A-Za-z\s'-]*?)"
            r"(?:[.!?,]|$)",
            message,
            re.IGNORECASE,
        )

        if location_match:

            location = self._clean_value(
                location_match.group(1)
            )

            # Ignore obviously invalid location values.
            invalid_locations = {
                "currently",
                "here",
                "there",
                "now",
            }

            if (
                location
                and location.lower()
                not in invalid_locations
            ):

                memories.append(
                    f"User lives in {location}."
                )

        # =================================================
        # FAVORITE
        # =================================================

        favorite_match = re.search(
            r"\bmy favou?rite\s+"
            r"(.+?)\s+is\s+"
            r"(.+?)(?:[.!?]|$)",
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
                    f"User's favorite "
                    f"{category} is {value}."
                )

        return memories

    # =====================================================
    # CLEAN VALUE
    # =====================================================

    def _clean_value(
        self,
        value: str,
    ) -> str:

        value = value.strip()

        value = value.rstrip(
            ".,!?"
        )

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