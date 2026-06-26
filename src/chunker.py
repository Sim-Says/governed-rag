import os

def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: The document text to chunk.
        chunk_size: Target size of each chunk in characters.
        overlap: Number of characters to overlap between chunks.
    
    Returns:
        List of text chunks.
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
            
        # Optional: prevent infinite loops if overlap is greater than or equal to chunk_size
        if overlap >= chunk_size:
            start += 1
            
    return chunks


def chunk_file(filepath: str, chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """Read a file and return chunks with metadata."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    filename = os.path.basename(filepath)
    chunks = chunk_document(text, chunk_size, overlap)
    
    return [
        {
            'id': f"{filename}_{i}",
            'text': chunk,
            'source': filename,
            'chunk_index': i
        }
        for i, chunk in enumerate(chunks)
    ]
