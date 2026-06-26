import json
from datetime import datetime
from pathlib import Path

class HITLCheckpoint:
    def __init__(self, faithfulness_threshold: float = 0.7, queue_dir: str = "data/hitl_queue"):
        self.threshold = faithfulness_threshold
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)
    
    def needs_review(self, result: dict) -> bool:
        """Check if a result needs human review based on faithfulness score."""
        return result['scores']['faithfulness'] < self.threshold
    
    def flag_for_review(self, result: dict):
        """Save a flagged result to the review queue."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result['query_id']}_{timestamp}.json"
        path = self.queue_dir / filename
        
        review_item = {
            'query_id': result['query_id'],
            'question': result.get('question', ''),
            'generated_answer': result.get('generated_answer', ''),
            'scores': result['scores'],
            'retrieved_chunks': result.get('retrieved_chunks', []),
            'flagged_at': datetime.now().isoformat(),
            'status': 'pending_review',
            'reviewer': None,
            'reviewed_answer': None
        }
        
        with open(path, 'w') as f:
            json.dump(review_item, f, indent=2)
    
    def get_pending_reviews(self) -> list[dict]:
        """Load all pending review items."""
        items = []
        for path in self.queue_dir.glob("*.json"):
            with open(path) as f:
                item = json.load(f)
                if item['status'] == 'pending_review':
                    items.append(item)
        return items
