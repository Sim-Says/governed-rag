import json
from pathlib import Path
from src.chunker import chunk_file
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline
from src.evaluator import RAGEvaluator
from src.reporter import EvalReporter

def load_corpus(docs_dir: str = "data/docs") -> list[dict]:
    """Load and chunk all documents from corpus."""
    all_chunks = []
    for filepath in sorted(Path(docs_dir).glob("*.md")):
        chunks = chunk_file(str(filepath))
        all_chunks.extend(chunks)
    return all_chunks

def load_golden(filepath: str = "data/golden/golden_qa.json") -> list[dict]:
    """Load golden Q&A dataset."""
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)

def run_evaluation():
    """Run full eval pipeline."""
    print("Loading corpus...")
    chunks = load_corpus()
    print(f"  {len(chunks)} chunks from {len(set(c['source'] for c in chunks))} documents")
    
    print("Building vector store...")
    store = VectorStore(persist_path="data/chroma_db")
    store.clear()  # fresh start
    store.add_chunks(chunks)
    
    print("Initializing RAG pipeline...")
    pipeline = RAGPipeline(store)
    
    print("Initializing evaluator...")
    evaluator = RAGEvaluator()
    
    print("Loading golden Q&A...")
    golden = load_golden()
    print(f"  {len(golden)} golden pairs")
    
    print("\nRunning evaluation...")
    results = []
    for pair in golden:
        print(f"  Evaluating {pair['id']}...", end=" ")
        
        # Run RAG
        rag_result = pipeline.ask(pair['question'])
        
        # Evaluate
        scores = evaluator.evaluate(rag_result, pair)
        pass_fail = evaluator.apply_thresholds(scores)
        needs_hitl = evaluator.needs_human_review(scores)
        
        overall = 'pass' if all(v == 'pass' for v in pass_fail.values()) else 'fail'
        
        result = {
            'query_id': pair['id'],
            'question': pair['question'],
            'generated_answer': rag_result['answer'],
            'reference_answer': pair['reference_answer'],
            'retrieved_chunks': [{'source': c['source'], 'chunk_index': c['chunk_index']} for c in rag_result['retrieved_chunks']],
            'scores': scores,
            'pass_fail': pass_fail,
            'overall': overall,
            'hitl_flag': needs_hitl
        }
        results.append(result)
        
        status = '[PASS]' if overall == 'pass' else '[FAIL]'
        print(f"{status} F:{scores['faithfulness']:.2f}")
    
    # Generate report
    reporter = EvalReporter()
    report = reporter.generate_report(results)
    path = reporter.save_report(report)
    reporter.print_summary(report)
    
    print(f"\nFull report saved to: {path}")
    return report

if __name__ == "__main__":
    run_evaluation()
