import os
from openai import OpenAI
from src.vector_store import VectorStore

SYSTEM_PROMPT = """You are a governance and compliance assistant. 
Answer the user's question using ONLY the provided context. 
If the context doesn't contain enough information, say "The provided context does not contain sufficient information to answer this question."
Always cite which source document your answer comes from."""

import httpx
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

class RAGPipeline:
    def __init__(self, vector_store: VectorStore, model: str = None):
        self.store = vector_store
        self.model = model or os.getenv("GENERATION_MODEL", "phi4-mini")
        http_client = httpx.Client(verify=False)
        self.client = OpenAI(
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1"),
            http_client=http_client
        )  # Ollama Cloud Pro — OpenAI-compatible API
    
    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve relevant chunks for a query."""
        return self.store.query(query, top_k=top_k)
    
    def generate(self, query: str, chunks: list[dict]) -> str:
        """Generate an answer using retrieved chunks as context."""
        context = "\n\n".join([
            f"[Source: {c['source']}, Chunk {c['chunk_index']}]\n{c['text']}"
            for c in chunks
        ])
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"}
            ],
            temperature=0.3  # low temperature = more deterministic, less creative
        )
        
        return response.choices[0].message.content
    
    def ask(self, query: str, top_k: int = 5) -> dict:
        """Full RAG pipeline: retrieve → generate → return with metadata."""
        chunks = self.retrieve(query, top_k=top_k)
        answer = self.generate(query, chunks)
        
        return {
            'query': query,
            'answer': answer,
            'retrieved_chunks': chunks
        }
