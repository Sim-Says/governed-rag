from src.vector_store import VectorStore

def test_vector_store_add_and_retrieve():
    store = VectorStore(persist_path="data/test_chroma")
    chunks = [
        {'id': 'test_0', 'text': 'The EU AI Act classifies AI systems by risk level.', 'source': 'test.md', 'chunk_index': 0},
        {'id': 'test_1', 'text': 'NIST AI RMF has four functions: Govern, Map, Measure, Manage.', 'source': 'test.md', 'chunk_index': 1},
    ]
    store.add_chunks(chunks)
    
    results = store.query("What are the NIST functions?", top_k=1)
    assert len(results) == 1
    assert 'NIST' in results[0]['text']
    
    store.clear()  # cleanup
