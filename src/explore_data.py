import pandas as pd

# --------------------------------------------------
# 1. Load dataset
# --------------------------------------------------

file_path = "data/raw/twcs.csv"

print("Loading dataset...")
df = pd.read_csv(file_path)

print("\n" + "=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)

print("Rows:", len(df))
print("Columns:", df.columns.tolist())


# --------------------------------------------------
# 2. Show first 5 rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("FIRST 5 ROWS")
print("=" * 60)

print(df.head())


# --------------------------------------------------
# 3. Check data types
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes)


# --------------------------------------------------
# 4. Check missing values
# --------------------------------------------------

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

print(df.isnull().sum())


# --------------------------------------------------
# 5. Check inbound distribution
# --------------------------------------------------

print("\n" + "=" * 60)
print("INBOUND DISTRIBUTION")
print("=" * 60)

print(df["inbound"].value_counts())

print("\nPercentage:")
print(df["inbound"].value_counts(normalize=True) * 100)


# --------------------------------------------------
# 6. Number of unique authors
# --------------------------------------------------

print("\n" + "=" * 60)
print("UNIQUE AUTHORS")
print("=" * 60)

print("Total unique authors:", df["author_id"].nunique())


# --------------------------------------------------
# 7. Most frequent authors overall
# --------------------------------------------------

print("\n" + "=" * 60)
print("TOP 30 AUTHORS OVERALL")
print("=" * 60)

print(df["author_id"].value_counts().head(30))


# --------------------------------------------------
# 8. Identify company/support accounts
# --------------------------------------------------
# inbound = False means the tweet was sent by the company/support account

company_tweets = df[df["inbound"] == False]

print("\n" + "=" * 60)
print("COMPANY/SUPPORT TWEETS")
print("=" * 60)

print("Total company/support tweets:", len(company_tweets))

print("\nTop 50 company/support accounts:")

company_counts = company_tweets["author_id"].value_counts()

print(company_counts.head(50))


# --------------------------------------------------
# 9. Save company account counts
# --------------------------------------------------

company_counts_df = company_counts.reset_index()

company_counts_df.columns = ["author_id", "tweet_count"]

company_counts_df.to_csv(
    "results/company_account_counts.csv",
    index=False
)

print("\nSaved company account counts to:")
print("results/company_account_counts.csv")


# --------------------------------------------------
# 10. Show customer vs company counts
# --------------------------------------------------

customer_tweets = df[df["inbound"] == True]

print("\n" + "=" * 60)
print("CUSTOMER VS COMPANY")
print("=" * 60)

print("Customer tweets:", len(customer_tweets))
print("Company tweets:", len(company_tweets))


# --------------------------------------------------
# 11. Basic text statistics
# --------------------------------------------------

print("\n" + "=" * 60)
print("TEXT STATISTICS")
print("=" * 60)

df["text_length"] = df["text"].astype(str).str.len()

print("Average tweet length:", round(df["text_length"].mean(), 2))
print("Shortest tweet:", df["text_length"].min())
print("Longest tweet:", df["text_length"].max())


# --------------------------------------------------
# 12. Check response relationships
# --------------------------------------------------

print("\n" + "=" * 60)
print("CONVERSATION / RESPONSE INFORMATION")
print("=" * 60)

response_count = df["response_tweet_id"].notna().sum()
in_response_count = df["in_response_to_tweet_id"].notna().sum()

print("Tweets with response_tweet_id:", response_count)
print("Tweets with in_response_to_tweet_id:", in_response_count)


# --------------------------------------------------
# 13. Check possible customer-company pairs
# --------------------------------------------------

# Customer tweets that received a response
customer_with_response = customer_tweets[
    customer_tweets["response_tweet_id"].notna()
]

print("\nCustomer tweets with a response:")
print(len(customer_with_response))


# --------------------------------------------------
# 14. Sample company accounts
# --------------------------------------------------

print("\n" + "=" * 60)
print("SAMPLE COMPANY ACCOUNTS")
print("=" * 60)

for account, count in company_counts.head(20).items():
    print(f"{account:30} {count}")


# --------------------------------------------------
# 15. Finish
# --------------------------------------------------

print("\n" + "=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)

print("Next step: choose a suitable support brand.")