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

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json

def build_embeddings_medium_kb(chunks_path, output_index_path, output_meta_path):
    """Build FAISS index optimized for medium KB"""
    
    # Load chunks
    with open(chunks_path) as f:
        chunks = json.load(f)
    
    print(f"Building embeddings for {len(chunks)} chunks...")
    
    # Generate embeddings
    model = SentenceTransformer("BAAI/bge-base-en-v1.5")
    
    texts = [chunk["text"] for chunk in chunks]
    
    # Add instruction prefix for better retrieval
    texts_with_instruction = [
        "Represent this document for retrieval: " + text 
        for text in texts
    ]
    
    embeddings = model.encode(
        texts_with_instruction, 
        normalize_embeddings=True,  # Important for cosine similarity
        show_progress_bar=True
    )
    
    embeddings = embeddings.astype('float32')
    
    # Choose index type based on size
    dimension = embeddings.shape[1]
    
    if len(chunks) < 1000:
        # Small-medium: Use flat index (exact search)
        index = faiss.IndexFlatIP(dimension)  # Inner Product (for normalized = cosine)
        print("Using Flat index (exact search)")
    else:
        # Medium-large: Use IVF for faster search
        nlist = 100  # Number of clusters
        quantizer = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
        
        # Train the index
        print("Training IVF index...")
        index.train(embeddings)
        print("Using IVF index (approximate search)")
    
    # Add embeddings
    index.add(embeddings)
    
    # Save index
    faiss.write_index(index, output_index_path)
    
    # Save metadata
    with open(output_meta_path, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"Index saved: {output_index_path}")
    print(f"Metadata saved: {output_meta_path}")
    print(f"Total vectors: {index.ntotal}")

if __name__ == "__main__":
    # musique KB paths
    chunks_path = "data/processed_chunks/musique_chunks.json"
    output_index_path = "embeddings/musique_faiss.index"
    output_meta_path = "embeddings/musique_metadata.json"

    # medium KB paths
    # chunks_path = "data/processed_chunks/hotpotqa_chunks.json"
    # output_index_path = "embeddings/hotpotqa_faiss.index"
    # output_meta_path = "embeddings/hotpotqa_metadata.json"

    # small KB paths
    # chunks_path = "data/processed_chunks/chunks.json"
    # output_index_path = "embeddings/faiss.index"
    # output_meta_path = "embeddings/chunk_meta.json"

    build_embeddings_medium_kb(
        chunks_path=chunks_path,
        output_index_path=output_index_path,
        output_meta_path=output_meta_path
    )