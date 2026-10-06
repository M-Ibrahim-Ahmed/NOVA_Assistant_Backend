
from app.services.memory_service import memory_service


USER_ID = "memory-update-test"


print("\nAdding first location...")

memory_service.add_memory(
    user_id=USER_ID,
    memory="User lives in Islamabad.",
)

print(
    memory_service.get_memories(USER_ID)
)


print("\nUpdating location...")

memory_service.add_memory(
    user_id=USER_ID,
    memory="User lives in Lahore.",
)

print(
    memory_service.get_memories(USER_ID)
)


print("\nAdding unrelated memory...")

memory_service.add_memory(
    user_id=USER_ID,
    memory="User likes football.",
)

print(
    memory_service.get_memories(USER_ID)
)
