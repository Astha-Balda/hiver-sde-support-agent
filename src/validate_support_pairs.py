import json
from collections import Counter

input_file = "data/processed/amazonhelp_support_pairs.jsonl"

total = 0
short_queries = 0
short_responses = 0
empty_queries = 0
empty_responses = 0

query_lengths = []
response_lengths = []

print("Validating support pairs...")

with open(input_file, "r", encoding="utf-8") as file:

    for line in file:

        if not line.strip():
            continue

        pair = json.loads(line)

        query = pair.get("query", "").strip()
        response = pair.get("response", "").strip()

        total += 1

        query_lengths.append(len(query))
        response_lengths.append(len(response))

        if not query:
            empty_queries += 1

        if not response:
            empty_responses += 1

        if len(query) < 10:
            short_queries += 1

        if len(response) < 10:
            short_responses += 1


print("\n" + "=" * 60)
print("SUPPORT PAIR QUALITY CHECK")
print("=" * 60)

print("Total pairs:", total)

print("\nQuery statistics:")
print("Average characters:",
      round(sum(query_lengths) / len(query_lengths), 2))

print("Shortest query:",
      min(query_lengths))

print("Longest query:",
      max(query_lengths))

print("\nResponse statistics:")
print("Average characters:",
      round(sum(response_lengths) / len(response_lengths), 2))

print("Shortest response:",
      min(response_lengths))

print("Longest response:",
      max(response_lengths))

print("\nPotential quality issues:")
print("Empty queries:", empty_queries)
print("Empty responses:", empty_responses)
print("Queries shorter than 10 chars:", short_queries)
print("Responses shorter than 10 chars:", short_responses)

print("\nValidation complete!")