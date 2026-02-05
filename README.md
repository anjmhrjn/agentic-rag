# Agent-Orchestrated Adaptive RAG for DevOps Knowledge System

## Overview

This project implements a **local Retrieval-Augmented Generation (RAG) system** for DevOps technical knowledge, using **agentic AI concepts**.  
It allows a user or agent to query DevOps documentation (architecture, runbooks, SOPs, incidents, postmortems, etc.) and receive accurate, context-aware answers with citations.

The system is fully local, runs on Apple Silicon (M1/M2/M5), and uses:

- **LLM**: Meta LLaMA 3.1 (GGUF format) via `llama.cpp`
- **Embeddings**: `sentence-transformers` (`BAAI/bge-base-en-v1.5`)
- **Vector database**: FAISS
- **Document management**: Markdown files with structured frontmatter

---

## Features

- RAG pipeline: query → retrieve relevant documents → generate answer
- Multiple `doc_type` support per document
- Citations of source documents
- Extensible: add new categories or doc_types without refactoring
- Fully local: no API costs

---

## Setup

1. **Clone repo**:

```bash
git clone <repo_url>
cd agentic_rag
```

2. **Install python dependencies**
```bash
pip install -r requirements.txt
```

3. **Download LLaMA GGUF model (local only, ~4.7GB) manually or via Hugging Face CLI**

4. **Prepare Documents**
Place Markdown files in data/raw_docs/ by category (if not present)
Ensure frontmatter includes doc_id, doc_type (list), category, service, date

5. **Build chunks**
```bash
python embeddings/build_chunks.py
```

6. **Build embeddings**
```bash
python embeddings/build_embeddings.py
```

---

## Usage
# Run baseline rag
```bash
python rag/baseline_rag.py
```

# Example query
query = "How do I troubleshoot a failed blue-green deployment?"
```bash
baseline_rag(query)
```

# Expected output
{
  "answer": "...",
  "sources": ["INC-007", "RUN-003"]
}

---

## Contributing

- Add new Markdown docs in `data/raw_docs/`
- Follow consistent `doc_type` conventions
- Run `build_chunks.py` → `build_embeddings.py` to update vector database

---

## Future Work

- Add **Agentic AI layer** for multi-step reasoning
- Support **multi-source synthesis**
- Implement **feedback/evaluation loop** for model answers
- Integrate CI/CD knowledge for live DevOps assistance

---

## License

MIT