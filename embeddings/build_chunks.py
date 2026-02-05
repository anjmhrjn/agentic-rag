import os
import json
import frontmatter
from llama_cpp import Llama

CHUNK_SIZE = 600
OVERLAP = 100

tokenizer = Llama(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")

def tokenize(text):
    return tokenizer.tokenize(text.encode("utf-8"))

def detokenize(tokens):
    return tokenizer.detokenize(tokens).decode("utf-8")

def chunk_text(text):
    tokens = tokenize(text)
    chunks = []

    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunks.append(detokenize(chunk_tokens))
        start += CHUNK_SIZE - OVERLAP

    return chunks

def process_docs(input_dir, output_file):
    all_chunks = []
    chunk_counter = {}

    for root, _, files in os.walk(input_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            path = os.path.join(root, file)
            post = frontmatter.load(path)

            meta = post.metadata
            text = post.content.strip()
            doc_id = meta["doc_id"]
            chunk_counter.setdefault(doc_id, 0)
            
            doc_type = meta.get("doc_type")
            if isinstance(doc_type, str):
                doc_type = [doc_type]

            for chunk in chunk_text(text):
                chunk_counter[doc_id] += 1
                all_chunks.append({
                    "chunk_id": f"{doc_id}_{chunk_counter[doc_id]:02d}",
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                    "service": meta.get("service", ""),
                    "text": chunk
                })

    with open(output_file, "w") as f:
        json.dump(all_chunks, f, indent=2)

if __name__ == "__main__":
    process_docs(
        input_dir="data/raw_docs",
        output_file="data/processed_chunks/chunks.json"
    )
