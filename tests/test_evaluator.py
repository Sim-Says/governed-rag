from src.evaluator import RAGEvaluator

def test_evaluator_returns_scores():
    evaluator = RAGEvaluator()
    
    result = {
        'query': 'What are the NIST functions?',
        'answer': 'The NIST AI RMF has four functions: Govern, Map, Measure, Manage.',
        'retrieved_chunks': [
            {'text': 'NIST AI RMF has four functions: Govern, Map, Measure, Manage.', 'source': 'test.md', 'chunk_index': 0}
        ]
    }
    reference = {
        'reference_answer': 'The NIST AI RMF consists of four functions: Govern, Map, Measure, and Manage.'
    }
    
    scores = evaluator.evaluate(result, reference)
    assert 'faithfulness' in scores
    assert 'answer_relevance' in scores
    assert 'context_relevance' in scores
    assert all(0 <= s <= 1 for s in scores.values())
