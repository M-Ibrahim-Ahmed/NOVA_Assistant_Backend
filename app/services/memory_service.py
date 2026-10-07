
import json
from pathlib import Path
from typing import List


# =========================================================
# MEMORY STORAGE PATH
# =========================================================

# Project root:
# C:\Users\MuhammadIbrahim\nova_backend
BASE_DIR = Path(__file__).resolve().parents[2]

# Persistent memory file:
# C:\Users\MuhammadIbrahim\nova_backend\data\nova_memory.json
MEMORY_FILE = BASE_DIR / "data" / "nova_memory.json"

MAX_MEMORIES_PER_USER = 50


class MemoryService:

    def __init__(self):
        self._ensure_storage()

    # =====================================================
    # STORAGE SETUP
    # =====================================================

    def _ensure_storage(self) -> None:

        MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not MEMORY_FILE.exists():

            with open(
                MEMORY_FILE,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    {},
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

    # =====================================================
    # LOAD MEMORIES
    # =====================================================

    def _load(self) -> dict:

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8",
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            FileNotFoundError,
        ):

            return {}

    # =====================================================
    # SAVE MEMORIES
    # =====================================================

    def _save(
        self,
        memories: dict,
    ) -> None:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                memories,
                file,
                indent=2,
                ensure_ascii=False,
            )

    # =====================================================
    # GET USER MEMORIES
    # =====================================================

    def get_memories(
        self,
        user_id: str,
    ) -> List[str]:

        memories = self._load()

        return memories.get(
            user_id,
            [],
        )

    # =====================================================
    # ADD / UPDATE MEMORY
    # =====================================================

    def add_memory(
        self,
        user_id: str,
        memory: str,
    ) -> None:

        memory = memory.strip()

        if not memory:
            return

        memories = self._load()

        if user_id not in memories:

            memories[user_id] = []

        existing = memories[user_id]

        # -------------------------------------------------
        # DETERMINE MEMORY CATEGORY
        # -------------------------------------------------

        category = self._get_memory_category(
            memory
        )

        # -------------------------------------------------
        # REPLACE CONFLICTING MEMORY
        # -------------------------------------------------

        if category:

            updated_memories = []

            for old_memory in existing:

                old_category = (
                    self._get_memory_category(
                        old_memory
                    )
                )

                if old_category == category:

                    # Remove the old fact because the
                    # new fact belongs to the same
                    # single-value category.
                    continue

                updated_memories.append(
                    old_memory
                )

            existing = updated_memories

        # -------------------------------------------------
        # AVOID EXACT DUPLICATES
        # -------------------------------------------------

        if memory in existing:
            return

        # -------------------------------------------------
        # ADD NEW MEMORY
        # -------------------------------------------------

        existing.append(memory)

        # -------------------------------------------------
        # LIMIT MEMORY COUNT
        # -------------------------------------------------

        memories[user_id] = existing[
            -MAX_MEMORIES_PER_USER:
        ]

        self._save(memories)

    # =====================================================
    # MEMORY CATEGORY
    # =====================================================

    def _get_memory_category(
        self,
        memory: str,
    ) -> str | None:

        normalized = memory.lower().strip()

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        if (
            normalized.startswith(
                "user's name is"
            )
            or normalized.startswith(
                "users name is"
            )
        ):
            return "name"

        # -------------------------------------------------
        # LOCATION
        # -------------------------------------------------

        if (
            normalized.startswith(
                "user lives in"
            )
            or normalized.startswith(
                "user is from"
            )
        ):
            return "location"

        # -------------------------------------------------
        # PROFESSION
        # -------------------------------------------------

        if normalized.startswith(
            "user works as"
        ):
            return "work"

        # -------------------------------------------------
        # FAVORITE
        # -------------------------------------------------

        if normalized.startswith(
            "user's favorite"
        ) or normalized.startswith(
            "users favorite"
        ):
            return "favorite"

        # -------------------------------------------------
        # DISLIKE
        # -------------------------------------------------

        if normalized.startswith(
            "user dislikes"
        ):
            return "dislike"

        # -------------------------------------------------
        # LIKE
        # -------------------------------------------------

        if normalized.startswith(
            "user likes"
        ):
            return "like"

        return None

    # =====================================================
    # DELETE MEMORY
    # =====================================================

    def delete_memory(
        self,
        user_id: str,
        memory: str,
    ) -> bool:

        memories = self._load()

        user_memories = memories.get(
            user_id,
            [],
        )

        if memory not in user_memories:
            return False

        user_memories.remove(memory)

        memories[user_id] = user_memories

        self._save(memories)

        return True

    # =====================================================
    # CLEAR ALL USER MEMORIES
    # =====================================================

    def clear_user_memories(
        self,
        user_id: str,
    ) -> None:

        memories = self._load()

        if user_id in memories:

            del memories[user_id]

            self._save(memories)


# =========================================================
# SINGLE MEMORY SERVICE INSTANCE
# =========================================================

memory_service = MemoryService()

