import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorRetriever:
    def __init__(self, index_path, meta_path, embed_model_name="BAAI/bge-base-en-v1.5"):
        self.index = faiss.read_index(index_path)
        with open(meta_path) as f:
            self.meta = json.load(f)
        self.embed_model = SentenceTransformer(embed_model_name)

    def retrieve(self, query, top_k=5, doc_type_filter=None):
        q_emb = self.embed_model.encode([query]).astype("float32")
        D, I = self.index.search(q_emb, top_k)
        results = []
        for idx in I[0]:
            chunk = self.meta[idx]
            if doc_type_filter:
                if not any(t in chunk["doc_type"] for t in doc_type_filter):
                    continue
            results.append(chunk)
        return results
