from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name: str = "data/models/all-MiniLM-L6-v2"):
        """Load the embedding model. 
        
        all-MiniLM-L6-v2 is a fast, lightweight model (384 dims).
        We point this to our local path to bypass SSL issues.
        """
        self.model = SentenceTransformer(model_name)
    
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Convert texts to embedding vectors."""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> list[float]:
        """Embed a single query for retrieval."""
        return self.model.encode([query])[0].tolist()
