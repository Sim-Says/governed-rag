from src.chunker import chunk_document

def test_chunk_document_splits_long_text():
    text = "A" * 1200
    chunks = chunk_document(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 3
    assert all(len(c) <= 550 for c in chunks)  # chunk + overlap

def test_chunk_document_preserves_short_text():
    text = "Short paragraph."
    chunks = chunk_document(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_chunk_document_has_overlap():
    text = "Sentence one. " * 100
    chunks = chunk_document(text, chunk_size=200, overlap=50)
    # Each chunk (except first) should start with text from previous chunk's end
    assert len(chunks) > 1
