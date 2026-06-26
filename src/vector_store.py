import chromadb
from src.embedder import Embedder

class VectorStore:
    def __init__(self, persist_path: str = "data/chroma_db"):
        self.embedder = Embedder()
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="governance_docs",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(self, chunks: list[dict]):
        """Add document chunks to the vector store."""
        texts = [c['text'] for c in chunks]
        embeddings = self.embedder.embed(texts)
        
        self.collection.add(
            ids=[c['id'] for c in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{'source': c['source'], 'chunk_index': c['chunk_index']} for c in chunks]
        )
    
    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        """Retrieve top-k chunks for a query."""
        query_embedding = self.embedder.embed_query(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
            
        return [
            {
                'text': results['documents'][0][i],
                'source': results['metadatas'][0][i]['source'],
                'chunk_index': results['metadatas'][0][i]['chunk_index'],
                'distance': results['distances'][0][i] if results['distances'] else 0.0
            }
            for i in range(len(results['documents'][0]))
        ]
    
    def clear(self):
        """Delete all chunks (for testing)."""
        self.client.delete_collection("governance_docs")
        self.collection = self.client.get_or_create_collection(
            name="governance_docs",
            metadata={"hnsw:space": "cosine"}
        )
