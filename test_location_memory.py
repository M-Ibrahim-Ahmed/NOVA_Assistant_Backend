from app.services.memory_extractor import memory_extractor


tests = [
    "I live in Islamabad.",
    "I moved to Lahore.",
    "I've moved to Dubai.",
    "I have moved to Karachi.",
    "I'm from Taxila.",
    "I live in currently.",
]


for message in tests:

    print("\nMessage:")
    print(message)

    print("Extracted:")
    print(
        memory_extractor.extract(message)
    )