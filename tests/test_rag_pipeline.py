from src.rag_pipeline import RAGPipeline
from src.vector_store import VectorStore

def test_rag_pipeline_generates_answer():
    store = VectorStore(persist_path="data/test_chroma")
    store.clear()
    store.add_chunks([
        {'id': 'test_0', 'text': 'The EU AI Act has four risk tiers: minimal, limited, high, unacceptable.', 'source': 'test.md', 'chunk_index': 0},
    ])
    
    pipeline = RAGPipeline(store)
    result = pipeline.ask("What are the risk tiers under the EU AI Act?")
    
    assert 'answer' in result
    assert 'retrieved_chunks' in result
    assert len(result['retrieved_chunks']) > 0
    assert 'risk' in result['answer'].lower() or 'tier' in result['answer'].lower()
    
    store.clear()
