from llm.local_llm import LocalLLM
from retriever.vector_retriever import VectorRetriever

def baseline_rag(query, top_k=5, doc_type_filter=None):
    retriever = VectorRetriever(
        index_path="embeddings/faiss.index",
        meta_path="embeddings/chunk_meta.json"
    )

    llm = LocalLLM(model_path="models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf")

    chunks = retriever.retrieve(query, top_k=top_k, doc_type_filter=doc_type_filter)
    context_docs = "\n".join([f"{c['doc_id']} [{','.join(c['doc_type'])}]: {c['text']}" for c in chunks])

    prompt = open("prompts/rag_prompt.txt").read().format(
        context_docs=context_docs,
        query=query
    )

    output = llm.generate(prompt)
    return output

if __name__ == "__main__":
    query = "How do I troubleshoot a failed blue-green deployment?"
    print(baseline_rag(query))
