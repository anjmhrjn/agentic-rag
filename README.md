# Agentic RAG for DevOps Knowledge Base

An intelligent Retrieval-Augmented Generation (RAG) system designed for DevOps documentation, featuring adaptive query routing, query decomposition, and self-evaluation capabilities. Built to run entirely locally with no API dependencies.

## 🎯 Overview

This project implements an **adaptive RAG pipeline** that intelligently routes queries through different strategies based on complexity and confidence. The system can handle simple lookups, complex multi-part questions, and even queries outside the knowledge base scope.

**Key Capabilities:**
- 🧠 Adaptive routing based on query complexity and retrieval confidence
- 🔍 Smart retrieval with relevance scoring
- 📊 Comprehensive evaluation framework with RAG-specific metrics
- 🤖 Optional query decomposition for complex questions
- ✅ Answer quality evaluation and self-correction
- 🚀 Fully local execution (no API calls)

## 🏗️ Architecture
```
User Query
    ↓
Query Classifier (determines doc types)
    ↓
Relevance Scoring (confidence check)
    ↓
Adaptive Routing:
  ├─ Simple queries → Standard RAG
  ├─ Complex queries → Enhanced RAG (more context)
  ├─ Multi-part queries → Query Decomposition
  └─ Low confidence → Lenient RAG / LLM-only
    ↓
Answer Generation with Citations
    ↓
Quality Evaluation (optional)
    ↓
Final Answer
```

## 🚀 Getting Started

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/anjmhrjn/agentic-rag.git
cd agentic-rag
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download the LLM model**
```bash
# Download Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
# Place in models/ directory
mkdir models
# Download from Hugging Face or use:
huggingface-cli download TheBloke/Llama-3-8B-Instruct-GGUF Meta-Llama-3-8B-Instruct-Q4_K_M.gguf --local-dir models/
```

4. **Prepare your documents**
```bash
# Place markdown files in data/raw_docs/
# Ensure frontmatter includes: doc_id, doc_type, category, date
```

5. **Build embeddings**
```bash
python embeddings/build_chunks.py
python embeddings/build_embeddings.py
```

### Usage

**Basic query:**
```python
from agents.orchestrator import AdaptiveRAGOrchestrator
from agents.query_classifier import QueryClassifierAgent
from retriever.vector_retriever import VectorRetriever
from llm.local_llm import LocalLLM

# Initialize components
llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
classifier = QueryClassifierAgent(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")
retriever = VectorRetriever(
    index_path="embeddings/faiss_index.bin",
    meta_path="embeddings/metadata.json"
)

# Create orchestrator (optimized for small KB)
orchestrator = AdaptiveRAGOrchestrator(
    classifier=classifier,
    retriever=retriever,
    llm=llm,
    kb_size="small",
    use_decomposition=False,  # Optional: enable for complex queries
    use_reflection=False      # Optional: enable for quality checks
)

# Query the system
result = orchestrator.process_query("How do I scale Kubernetes pods?")

print(f"Answer: {result['answer']}")
print(f"Sources: {result['sources']}")
print(f"Strategy: {result['strategy']}")
print(f"Confidence: {result['confidence']:.3f}")
```

## 🔧 Configuration

The system adapts based on knowledge base size:
```python
# Small KB (< 500 docs) - recommended for 80 doc KB
orchestrator = AdaptiveRAGOrchestrator(
    ...,
    kb_size="small",
    use_decomposition=False,  # Overhead not worth it
    use_reflection=False      # Adds latency without benefit
)

# Medium KB (500-5000 docs)
orchestrator = AdaptiveRAGOrchestrator(
    ...,
    kb_size="medium",
    use_decomposition=True,   # Helps with complex queries
    use_reflection=True       # Improves quality
)

# Large KB (5000+ docs)
orchestrator = AdaptiveRAGOrchestrator(
    ...,
    kb_size="large",
    use_decomposition=True,
    use_reflection=True
)
```

## 🧪 Evaluation Framework

The project includes a comprehensive evaluation suite:
```bash
# Run single benchmark
python -m evaluation.run_eval

# Compare configurations
python -m evaluation.compare
```

**Metrics tracked:**
- Critical Source Recall (did we find important docs?)
- Mean Reciprocal Rank (how quickly?)
- Success@k (was relevant doc in top-k?)
- Citation Accuracy (valid citations?)
- Topic Coverage (answer completeness)

## 📝 Document Format

Documents should be markdown files with YAML frontmatter:
```markdown
---
doc_id: RUN-003
doc_type:
  - runbook
  - kubernetes
category: operations
service: kubernetes
date: 2024-01-15
---

# How to Scale Kubernetes Pods

To scale a Kubernetes deployment...
```

## 🔑 Key Features

### 1. Adaptive Query Routing
- **Standard RAG**: High confidence, simple queries
- **Complex RAG**: High confidence, complex queries (more context)
- **Decomposed RAG**: Multi-part queries split into sub-queries
- **Lenient RAG**: Low confidence (wider retrieval threshold)
- **LLM-only**: No relevant documentation (general knowledge)

### 2. Query Intelligence
- Automatic doc type classification
- Complexity detection
- Query decomposition for multi-part questions
- Context preservation in sub-queries

### 3. Self-Evaluation
- Citation validation (detects hallucinated doc IDs)
- Relevance checking
- Contextual support verification
- Automatic re-generation on poor quality

### 4. Small KB Optimization
- No doc type filtering (casts wider net)
- Lower similarity thresholds
- Smart fallbacks when filters too restrictive
- Fast retrieval (optimized for 50-500 docs)

## 🛠️ Technologies Used

- **LLM**: Meta Llama 3 8B (GGUF format via llama-cpp-python)
- **Embeddings**: BAAI/bge-base-en-v1.5 (sentence-transformers)
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Document Format**: Markdown with YAML frontmatter

## 🚧 Known Limitations

1. **Citation Format Compliance**: LLM sometimes uses "according to DOC-ID" instead of [DOC-ID]
2. **Small Model Constraints**: 8B model struggles with strict formatting rules
3. **Latency**: Local inference slower than API-based solutions
4. **KB Size**: Optimized for small knowledge bases (50-500 docs)

## 📄 License

MIT License - see LICENSE file for details

---

**Note**: This system is optimized for small knowledge bases (80 docs). For larger KBs, enable decomposition and reflection features in the configuration.