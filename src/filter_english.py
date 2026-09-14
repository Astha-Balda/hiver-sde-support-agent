import json
import re
import os


# --------------------------------------------------
# 1. Load conversations
# --------------------------------------------------

input_file = "data/processed/amazonhelp_conversations.jsonl"

print("Loading conversations...")

conversations = []

with open(input_file, "r", encoding="utf-8") as file:

    for line in file:
        conversations.append(json.loads(line))

print("Total conversations:", len(conversations))


# --------------------------------------------------
# 2. English detection
# --------------------------------------------------

from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


def is_english(text):
    text = str(text).strip()

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove usernames
    text = re.sub(r"@\w+", "", text)

    # Very short messages are unreliable
    if len(text) < 5:
        return True

    try:
        return detect(text) == "en"
    except:
        return False


# --------------------------------------------------
# 3. Filter conversations
# --------------------------------------------------

english_conversations = []

for conversation in conversations:

    messages = conversation["messages"]

    customer_messages = [
        message
        for message in messages
        if message["inbound"]
    ]

    # Ignore conversations without customer messages
    if not customer_messages:
        continue

    # Check customer messages only.
    english_count = 0

    for message in customer_messages:

        if is_english(message["text"]):
            english_count += 1

    # Keep conversation if at least 80% of customer
    # messages are English.
    english_ratio = (
        english_count / len(customer_messages)
    )

    if english_ratio >= 0.80:

        english_conversations.append(conversation)


# --------------------------------------------------
# 4. Statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("ENGLISH FILTER RESULTS")
print("=" * 60)

print(
    "Original conversations:",
    len(conversations)
)

print(
    "English conversations:",
    len(english_conversations)
)

print(
    "Removed conversations:",
    len(conversations) - len(english_conversations)
)

if conversations:

    percentage = (
        len(english_conversations)
        / len(conversations)
        * 100
    )

    print(
        "English percentage:",
        round(percentage, 2),
        "%"
    )


# --------------------------------------------------
# 5. Count customer messages
# --------------------------------------------------

customer_count = 0

for conversation in english_conversations:

    for message in conversation["messages"]:

        if message["inbound"]:
            customer_count += 1


print(
    "English customer messages:",
    customer_count
)


# --------------------------------------------------
# 6. Show examples
# --------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE ENGLISH CONVERSATIONS")
print("=" * 60)

for i, conversation in enumerate(
    english_conversations[:5]
):

    print("\nConversation", i + 1)

    for message in conversation["messages"]:

        speaker = (
            "CUSTOMER"
            if message["inbound"]
            else "AMAZONHELP"
        )

        print(
            f"[{speaker}] {message['text']}"
        )


# --------------------------------------------------
# 7. Save English conversations
# --------------------------------------------------

os.makedirs("data/processed", exist_ok=True)

output_file = (
    "data/processed/"
    "amazonhelp_english_conversations.jsonl"
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    for conversation in english_conversations:

        file.write(
            json.dumps(
                conversation,
                ensure_ascii=False
            ) + "\n"
        )


print("\nSaved English conversations to:")
print(output_file)

print("\nEnglish filtering complete!")