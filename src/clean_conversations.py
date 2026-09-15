import json
import re
import os


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

input_file = "data/processed/amazonhelp_english_conversations.jsonl"

output_file = "data/processed/amazonhelp_cleaned.jsonl"


# --------------------------------------------------
# 2. Clean text
# --------------------------------------------------

def clean_text(text):
    """
    Clean a customer-support message while preserving
    the actual meaning of the message.
    """

    text = str(text)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove Twitter usernames/mentions
    text = re.sub(r"@\w+", "", text)

    # Remove AmazonHelp agent signatures such as ^TN
    text = re.sub(r"\^[A-Za-z]{1,3}\b", "", text)

    # Replace HTML entities
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    text = text.replace("&amp;", "&")

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


# --------------------------------------------------
# 3. Process conversations
# --------------------------------------------------

print("Loading English conversations...")

processed_count = 0
removed_count = 0

os.makedirs("data/processed", exist_ok=True)


with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_file, "w", encoding="utf-8") as outfile:

    for line in infile:

        if not line.strip():
            continue

        conversation = json.loads(line)

        cleaned_messages = []

        for message in conversation["messages"]:

            cleaned = clean_text(message["text"])

            # Skip messages that become empty
            if not cleaned:
                continue

            cleaned_message = message.copy()
            cleaned_message["text"] = cleaned

            cleaned_messages.append(cleaned_message)

        # Keep conversation only if messages remain
        if cleaned_messages:

            conversation["messages"] = cleaned_messages

            outfile.write(
                json.dumps(
                    conversation,
                    ensure_ascii=False
                ) + "\n"
            )

            processed_count += 1

        else:
            removed_count += 1


# --------------------------------------------------
# 4. Statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("CLEANING RESULTS")
print("=" * 60)

print("Processed conversations:", processed_count)
print("Removed empty conversations:", removed_count)

print("\nSaved cleaned conversations to:")
print(output_file)

print("\nCleaning complete!")