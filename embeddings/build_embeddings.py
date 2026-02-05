import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-base-en-v1.5"
INDEX_PATH = "embeddings/faiss.index"
META_PATH = "embeddings/chunk_meta.json"

model = SentenceTransformer(MODEL_NAME)

with open("data/processed_chunks/chunks.json") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings).astype("float32"))

faiss.write_index(index, INDEX_PATH)

with open(META_PATH, "w") as f:
    json.dump(chunks, f, indent=2)

print(f"Indexed {len(chunks)} chunks.")
