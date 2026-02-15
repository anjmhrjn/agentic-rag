import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorRetriever:
    def __init__(self, index_path, meta_path, embed_model_name="BAAI/bge-base-en-v1.5"):
        self.index = faiss.read_index(index_path)
        with open(meta_path) as f:
            self.meta = json.load(f)
        # Initialize embedding model
        self.embed_model = SentenceTransformer(embed_model_name)
        # Normalize instruction for BGE models (improves retrieval)
        self.query_instruction = "Represent this query for searching relevant DevOps documentation: "

    def retrieve(
        self, 
        query, 
        top_k = 5, 
        doc_type_filter = None,
        similarity_threshold = 0.0,
        retrieval_multiplier = 3
    ):
        # Encode query with instruction (improves BGE performance)
        q_text = self.query_instruction + query
        q_emb = self.embed_model.encode([q_text], normalize_embeddings=True).astype("float32")
        
        # Retrieve more results if filtering is needed
        initial_k = top_k * retrieval_multiplier if doc_type_filter else top_k
        initial_k = min(initial_k, self.index.ntotal)  # Don't exceed index size
        
        # Search FAISS index
        distances, indices = self.index.search(q_emb, initial_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
            
            chunk = self.meta[idx].copy()
            
            # Apply doc_type filter
            if doc_type_filter:
                chunk_types = chunk.get("doc_type", [])
                if isinstance(chunk_types, str):
                    chunk_types = [chunk_types]
                if not any(dt in doc_type_filter for dt in chunk_types):
                    continue
            
            # Convert distance to similarity score (for normalized embeddings)
            # FAISS L2 distance -> cosine similarity: 1 - (distance^2 / 2)
            similarity = 1 - (dist / 2)
            
            # Apply similarity threshold
            if similarity < similarity_threshold:
                continue
            
            # Add score to chunk metadata
            chunk["similarity_score"] = float(similarity)
            chunk["distance"] = float(dist)
            
            results.append(chunk)
            
            # Stop once we have enough filtered results
            if len(results) >= top_k:
                break
        
        return results
    
    def retrieve_batch(
        self, 
        queries, 
        top_k = 5,
        doc_type_filter = None
    ):
        q_texts = [self.query_instruction + q for q in queries]
        q_embs = self.embed_model.encode(q_texts, normalize_embeddings=True).astype("float32")
        
        initial_k = top_k * 3 if doc_type_filter else top_k
        initial_k = min(initial_k, self.index.ntotal)
        
        distances, indices = self.index.search(q_embs, initial_k)
        
        all_results = []
        for q_dists, q_indices in zip(distances, indices):
            results = []
            for dist, idx in zip(q_dists, q_indices):
                if idx == -1:
                    continue
                
                chunk = self.meta[idx].copy()
                
                if doc_type_filter:
                    chunk_types = chunk.get("doc_type", [])
                    if isinstance(chunk_types, str):
                        chunk_types = [chunk_types]
                    if not any(dt in doc_type_filter for dt in chunk_types):
                        continue
                
                similarity = 1 - (dist / 2)
                chunk["similarity_score"] = float(similarity)
                chunk["distance"] = float(dist)
                
                results.append(chunk)
                
                if len(results) >= top_k:
                    break
            
            all_results.append(results)
        
        return all_results

    def get_relevance_score(self, query, top_k = 5):
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return 0.0
        
        avg_score = np.mean([r["similarity_score"] for r in results])
        return float(avg_score)