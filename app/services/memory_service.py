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

        # Create the data directory if it does not exist.
        MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Create the memory file if it does not exist.
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
    # ADD MEMORY
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

        # Avoid exact duplicates.
        if memory in existing:
            return

        existing.append(memory)

        # Keep storage bounded.
        memories[user_id] = existing[
            -MAX_MEMORIES_PER_USER:
        ]

        self._save(memories)

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