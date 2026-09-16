# ResolveAI: AI Customer Support Agent

An AI-powered customer support system that uses semantic search and Retrieval-Augmented Generation (RAG) to retrieve relevant historical support cases and generate context-aware responses to customer queries.

The project is designed to demonstrate an end-to-end AI support workflow including data preprocessing, semantic retrieval, confidence-based handling, and eventually LLM-powered response generation.

---

## 🚀 Project Overview

Customer support teams handle a large number of repetitive queries related to orders, deliveries, payments, refunds, returns, accounts, and other issues.

This project uses historical customer-support conversations to build an intelligent support agent that can:

- Understand the meaning of a customer's query
- Retrieve similar historical support cases
- Use relevant support information as context
- Generate a grounded response using an LLM
- Detect low-confidence retrievals
- Escalate queries when relevant information cannot be found

---

## 🏗️ System Architecture


Customer Query
      │
      ▼
Text Processing
      │
      ▼
Sentence Transformer
      │
      ▼
Query Embedding
      │
      ▼
FAISS Vector Search
      │
      ▼
Relevant Historical Support Cases
      │
      ▼
Similarity / Confidence Check
      │
      ├─────────────── Low Confidence
      │                      │
      │                      ▼
      │                 Ask / Escalate
      │
      ▼
Retrieved Context
      │
      ▼
RAG + LLM
      │
      ▼
Grounded Support Response


✨ Features
Data Processing:
Processes customer-support conversations from the TWCS dataset
Filters conversations based on English-language content
Cleans URLs, mentions, signatures, and unnecessary whitespace
Converts conversations into customer-query and agent-response pairs
Performs basic intent and issue analysis
Validates generated support pairs

Semantic Search:
Generates sentence embeddings using all-MiniLM-L6-v2
Creates 384-dimensional embeddings
Uses FAISS for efficient similarity search
Retrieves the most relevant historical support cases
Uses cosine-style similarity through normalized embeddings

Confidence Handling:
Applies a similarity threshold to retrieved results
Accepts sufficiently relevant historical cases
Detects low-confidence queries
Provides a fallback path for clarification or escalation

RAG-based Response Generation:
The planned RAG layer will use retrieved historical support cases as context for an LLM, reducing the likelihood of generating unsupported responses.

API and User Interface:

The planned application will provide:

FastAPI backend
REST APIs for customer queries
React.js frontend
Real-time support interaction
Confidence-based fallback and escalation
📊 Dataset

This project uses the Twitter Customer Support (TWCS) dataset containing customer-service conversations between users and support accounts.

For the current processing pipeline:

Original conversations processed: 82,556
English conversations retained: 60,531
Customer messages extracted: 93,547
Customer-agent support pairs created: 93,544
Embedding dimension: 384

The raw dataset is intentionally excluded from the repository because of its size and dataset distribution considerations.

🛠️ Tech Stack
Programming Language
Python
Machine Learning / NLP
Sentence Transformers
Hugging Face Transformers
Natural Language Processing
Text Embeddings
Vector Search
FAISS
Backend
FastAPI
REST APIs
Frontend
React.js
AI Architecture
Retrieval-Augmented Generation (RAG)
Large Language Models (LLMs)
Semantic Search
Development Tools
Git
GitHub
VS Code

📁 Project Structure
hiver-sde-support-agent/
│
├── data/
│   ├── raw/
│   │   └── twcs.csv
│   │
│   └── processed/
│       ├── amazonhelp_english_conversations.jsonl
│       ├── amazonhelp_cleaned.jsonl
│       ├── amazonhelp_support_pairs.jsonl
│       ├── support_pairs.index
│       └── support_pairs_metadata.json
│
├── src/
│   ├── filter_english.py
│   ├── clean_conversations.py
│   ├── create_support_pairs.py
│   ├── analyze_intents.py
│   ├── validate_support_pairs.py
│   ├── build_vector_index.py
│   └── search_support.py
│
├── .gitignore
├── requirements.txt
└── README.md

👩‍💻 Author

Astha Balda

Computer Science Engineering Student
