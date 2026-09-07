from app.services.memory_extractor import memory_extractor


test_messages = [
    "My name is Ibrahim.",
    "I like football.",
    "I love programming.",
    "I don't like spicy food.",
    "I work as a software developer and Cyber Security Expert.",
    "I live in Islamabad.",
    "My favorite programming language is Python.",
]


for message in test_messages:

    memories = memory_extractor.extract(message)

    print(f"\nMessage: {message}")

    for memory in memories:
        print(f"Memory: {memory}")