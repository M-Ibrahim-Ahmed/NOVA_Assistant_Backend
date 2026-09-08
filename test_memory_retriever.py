from app.services.memory_retriever import memory_retriever


memories = [
    "User's name is Ibrahim.",
    "User likes football.",
    "User's favorite programming language is python.",
    "User lives in Islamabad.",
    "User works as a software developer.",
]


test_messages = [
    "What is my name?",
    "What sport do I like?",
    "What programming language do I like?",
    "Where do I live?",
    "What do I do for work?",
]


for message in test_messages:

    print("\n" + "=" * 50)

    print(
        f"Message: {message}"
    )

    results = memory_retriever.retrieve(
        message=message,
        memories=memories,
        max_results=5,
    )

    print("Relevant memories:")

    for memory in results:

        print(
            f"- {memory}"
        )