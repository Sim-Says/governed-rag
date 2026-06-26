from src.hitl import HITLCheckpoint
import os
import shutil

def test_low_confidence_gets_flagged():
    checkpoint = HITLCheckpoint(faithfulness_threshold=0.7)
    result = {
        'query_id': 'q001',
        'scores': {'faithfulness': 0.5, 'answer_relevance': 0.9, 'context_relevance': 0.8},
        'generated_answer': 'This might be hallucinated.'
    }
    assert checkpoint.needs_review(result) == True

def test_high_confidence_passes():
    checkpoint = HITLCheckpoint(faithfulness_threshold=0.7)
    result = {
        'query_id': 'q001',
        'scores': {'faithfulness': 0.85, 'answer_relevance': 0.9, 'context_relevance': 0.8},
        'generated_answer': 'This is grounded.'
    }
    assert checkpoint.needs_review(result) == False

def test_flagged_answer_saved_to_queue():
    queue_dir = "data/test_hitl_queue"
    # Ensure clean state
    if os.path.exists(queue_dir):
        shutil.rmtree(queue_dir)
        
    checkpoint = HITLCheckpoint(faithfulness_threshold=0.7, queue_dir=queue_dir)
    result = {
        'query_id': 'q001',
        'question': 'What is the EU AI Act?',
        'scores': {'faithfulness': 0.5, 'answer_relevance': 0.9, 'context_relevance': 0.8},
        'generated_answer': 'Possibly wrong answer.',
        'retrieved_chunks': []
    }
    checkpoint.flag_for_review(result)
    files = os.listdir(queue_dir)
    assert len(files) > 0
