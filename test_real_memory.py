from app.services.memory_service import memory_service
from app.services.memory_retriever import memory_retriever


USER_ID = "246c9112-d338-4d0d-8881-526517b0cd44"


memories = memory_service.get_memories(
    USER_ID
)

print("\nALL MEMORIES:")
for memory in memories:
    print("-", memory)


tests = [
    "Where do I live?",
    "What city do I live in?",
    "Where am I from?",
    "What is my name?",
    "What programming language do I like?",
]


for message in tests:

    print("\n" + "=" * 60)

    print("QUESTION:")
    print(message)

    results = memory_retriever.retrieve(
        message=message,
        memories=memories,
        max_results=5,
    )

    print("\nRELEVANT MEMORIES:")

    for memory in results:
        print("-", memory)