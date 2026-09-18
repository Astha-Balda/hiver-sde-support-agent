# ResolveAI 🤖

**AI-Powered Customer Support Agent using RAG**

ResolveAI is an AI-powered customer support application that uses **Retrieval-Augmented Generation (RAG)** to provide relevant and natural responses to customer queries.

The system retrieves similar historical customer-support conversations using **FAISS** and **Sentence Transformers**, then provides the retrieved context to a **Groq-hosted LLM** to generate a concise support response.

---

## 🚀 Features

* 💬 AI-powered customer support chat
* 🔎 Semantic search using FAISS
* 🧠 Sentence Transformer embeddings
* 📚 Retrieval-Augmented Generation (RAG)
* ⚡ Groq-powered response generation
* 🎯 Similarity-based confidence threshold
* ❓ Multi-question query handling
* 🛡️ Low-confidence fallback responses
* 🔐 Environment-variable based API key management
* 🌐 React-based responsive frontend
* 🔗 FastAPI backend
* 📡 REST API communication between frontend and backend

---

## 🏗️ System Architecture

```text
┌──────────────────────┐
│    React Frontend    │
│      ResolveAI       │
└──────────┬───────────┘
           │
           │ HTTP Request
           ▼
┌──────────────────────┐
│    FastAPI Backend   │
│      /support        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    Support Agent     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Sentence Transformer│
│  Query Embedding     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       FAISS          │
│ Semantic Retrieval   │
└──────────┬───────────┘
           │
           │ Relevant
           │ Support Cases
           ▼
┌──────────────────────┐
│     Groq LLM         │
│ Response Generation  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│    AI Response       │
│    React Frontend    │
└──────────────────────┘
```

---

## 🧠 How It Works

### 1. User Query

The customer enters a support question through the ResolveAI chat interface.

Example:

```text
My payment failed. What should I do?
```

### 2. Query Embedding

The query is converted into a numerical vector using the **Sentence Transformer `all-MiniLM-L6-v2`** model.

### 3. Semantic Retrieval

The generated embedding is searched against the FAISS vector index.

The system retrieves the most similar historical customer-support cases.

### 4. Confidence Check

The best similarity score is compared against a predefined threshold:

```text
Similarity Threshold = 0.75
```

If the similarity score is below the threshold, the system does not generate an unsupported answer and instead returns a fallback response.

### 5. Context Construction

For relevant queries, the retrieved customer-support examples are provided as context to the LLM.

### 6. Response Generation

The Groq-hosted LLM generates a concise and natural response based on the retrieved support information.

### 7. Response to User

The generated response is returned through the FastAPI API and displayed in the React frontend.

---

## ❓ Multi-Question Handling

ResolveAI can handle multiple questions in a single customer message.

Example:

```text
My payment failed? Where is my refund? My package says delivered but I didn't receive it?
```

The system:

1. Splits the message into individual questions.
2. Performs retrieval separately for each question.
3. Filters irrelevant questions using the similarity threshold.
4. Combines the relevant retrieved context.
5. Uses a single LLM call to generate the responses.
6. Returns the answers in the same order.

This reduces unnecessary LLM calls compared with generating a separate response for every question.

---

## 🛡️ Hallucination Control

ResolveAI uses several safeguards to reduce unsupported responses:

* Retrieves historical support information before generation.
* Uses a similarity threshold of `0.75`.
* Rejects low-confidence queries.
* Instructs the LLM to answer only using retrieved information.
* Prevents the model from inventing account details, order information, refunds, dates, or policies.
* Uses fallback responses when relevant information cannot be found.

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* HTML
* CSS

### Backend

* Python
* FastAPI
* Pydantic

### AI / Machine Learning

* Sentence Transformers
* `all-MiniLM-L6-v2`
* FAISS
* Retrieval-Augmented Generation (RAG)
* Groq API
* `openai/gpt-oss-20b`

### Data

* Customer support conversation dataset
* JSONL processed support pairs
* FAISS vector index

### Development Tools

* Git
* GitHub
* VS Code
* Postman

---

## 📂 Project Structure

```text
hiver-sde-support-agent/
│
├── data/
│   ├── raw/
│   │   └── twcs.csv
│   │
│   └── processed/
│       ├── support_pairs.index
│       └── support_pairs_metadata.json
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── src/
│   ├── api.py
│   ├── support_agent.py
│   ├── retriever.py
│   └── ...
│
├── .gitignore
├── requirements.txt
├── README.md
└── ...
```

> **Note:** The raw dataset, processed datasets, FAISS index files, environment files, and other generated files should not be committed if they are included in `.gitignore`.

---

## ⚙️ Local Setup

### Prerequisites

Make sure you have installed:

* Python 3.10+
* Node.js
* npm
* Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/Astha-Balda/hiver-sde-support-agent.git
cd hiver-sde-support-agent
```

---

### 2. Create and Activate Virtual Environment

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

If Groq is not already included in `requirements.txt`:

```bash
pip install groq
```

---

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit the `.env` file to GitHub.

---

### 5. Start the Backend

From the project root:

```bash
uvicorn src.api:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

---

### 6. Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

## 🔌 API

### Health Check

```http
GET /
```

Example response:

```json
{
  "message": "Hiver SDE Support Agent API is running"
}
```

### Generate Support Response

```http
POST /support
```

Request:

```json
{
  "query": "My payment failed"
}
```

Response:

```json
{
  "query": "My payment failed",
  "confidence": "HIGH",
  "similarity": 0.84,
  "retrieved_cases": 3,
  "response": "I'm sorry to hear your payment failed. Please share any error message you received so we can better understand the issue and assist you."
}
```

---

## 📊 Retrieval & Confidence

ResolveAI uses cosine similarity between the query embedding and stored support-case embeddings.

The current confidence rule is:

```text
Similarity >= 0.75  → HIGH confidence
Similarity < 0.75   → LOW confidence
```

Low-confidence queries receive a fallback response instead of being passed to the LLM.

---

## 🔐 Security

* API keys are stored using environment variables.
* `.env` files are excluded from Git.
* Large raw datasets are excluded from the repository.
* Generated processed files and vector indexes can be regenerated locally.

---

## 🎯 Use Cases

ResolveAI can be used for:

* E-commerce customer support
* Order and delivery queries
* Payment-related support
* Refund-related queries
* Return and cancellation queries
* Customer-service automation
* FAQ assistance
* Support ticket response generation

---

## 🔮 Future Improvements

Potential improvements include:

* Better handling of noisy or typo-filled queries
* More advanced query splitting
* Conversation memory
* Streaming AI responses
* Authentication and user accounts
* Support ticket creation
* Improved retrieval and reranking
* Evaluation metrics for retrieval and response quality
* Production monitoring and logging
* Cloud deployment

---

## 📌 Project Status

**Status: Completed**

The application currently supports:

* React frontend
* FastAPI backend
* FAISS semantic retrieval
* RAG-based response generation
* Groq LLM integration
* Confidence-based fallback
* Multi-question handling
* End-to-end frontend/backend integration

**Deployment is the remaining step.**

---

## 👩‍💻 Author

**Astha Balda**

B.E. Computer Science & Engineering
Chitkara University

---

## ⭐ Acknowledgements

* FAISS for efficient vector similarity search
* Sentence Transformers for text embeddings
* Groq for LLM inference
* FastAPI for backend API development
* React for the frontend application
