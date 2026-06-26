import json
from datetime import datetime
from pathlib import Path

class EvalReporter:
    def __init__(self, output_dir: str = "data/results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, results: list[dict]) -> dict:
        """Generate summary report from eval results."""
        total = len(results)
        passed = sum(1 for r in results if r['overall'] == 'pass')
        failed = total - passed
        hitl_flagged = sum(1 for r in results if r['hitl_flag'])
        
        scores = [r['scores'] for r in results]
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': total,
            'passed': passed,
            'failed': failed,
            'hitl_flagged': hitl_flagged,
            'scores_summary': {
                'faithfulness_mean': sum(s['faithfulness'] for s in scores) / total if total else 0,
                'answer_relevance_mean': sum(s['answer_relevance'] for s in scores) / total if total else 0,
                'context_relevance_mean': sum(s['context_relevance'] for s in scores) / total if total else 0,
            }
        }
        
        return {
            'summary': summary,
            'results': results
        }
    
    def save_report(self, report: dict, filename: str = None):
        """Save report to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_{timestamp}.json"
        
        path = self.output_dir / filename
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(path)
    
    def print_summary(self, report: dict):
        """Print human-readable summary to console."""
        s = report['summary']
        print(f"\n{'='*60}")
        print(f"  EVAL REPORT — {s['timestamp']}")
        print(f"{'='*60}")
        print(f"  Total: {s['total_queries']}  Passed: {s['passed']}  Failed: {s['failed']}")
        print(f"  HITL Flagged: {s['hitl_flagged']}")
        print(f"{'='*60}")
        print(f"  Faithfulness:        {s['scores_summary']['faithfulness_mean']:.3f}")
        print(f"  Answer Relevance:    {s['scores_summary']['answer_relevance_mean']:.3f}")
        print(f"  Context Relevance:   {s['scores_summary']['context_relevance_mean']:.3f}")
        print(f"{'='*60}\n")
        
        for r in report['results']:
            status = '[PASS]' if r['overall'] == 'pass' else '[FAIL]'
            hitl = ' (HITL)' if r['hitl_flag'] else ''
            print(f"  {status} {r['query_id']} — F:{r['scores']['faithfulness']:.2f} AR:{r['scores']['answer_relevance']:.2f} CR:{r['scores']['context_relevance']:.2f}{hitl}")
            print(f"     Q: {r['question'][:80]}")
