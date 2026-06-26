import os
import httpx
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from datasets import Dataset
from dotenv import load_dotenv

load_dotenv()

class RAGEvaluator:
    def __init__(self, thresholds: dict = None):
        self.thresholds = thresholds or {
            'faithfulness': 0.7,
            'answer_relevance': 0.7,
            'context_relevance': 0.6
        }
    
    def evaluate(self, rag_result: dict, golden_pair: dict) -> dict:
        """Run RAG triad evaluation on a single result.
        
        Args:
            rag_result: Output from RAGPipeline.ask() — has query, answer, retrieved_chunks.
            golden_pair: Entry from golden_qa.json — has reference_answer.
        
        Returns:
            Dict of scores: {faithfulness, answer_relevance, context_relevance}
        """
        # Configure Ollama Cloud Pro as the Ragas judge LLM
        http_client = httpx.Client(verify=False)
        http_async_client = httpx.AsyncClient(verify=False)
        chat = ChatOpenAI(
            api_key=os.getenv("OLLAMA_API_KEY", "ollama"),
            base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1"),
            model=os.getenv("JUDGE_MODEL", "ministral-3:8b"),
            http_client=http_client,
            http_async_client=http_async_client
        )
        judge_llm = LangchainLLMWrapper(chat)
        
        # Configure local embeddings for metrics that need it (like answer_relevancy)
        emb = HuggingFaceEmbeddings(model_name='data/models/all-MiniLM-L6-v2')
        judge_embeddings = LangchainEmbeddingsWrapper(emb)
        
        # Build Ragas evaluation dataset
        eval_data = {
            'question': [rag_result['query']],
            'answer': [rag_result['answer']],
            'contexts': [[c['text'] for c in rag_result['retrieved_chunks']]],
            'ground_truth': [golden_pair['reference_answer']]
        }
        
        dataset = Dataset.from_dict(eval_data)
        
        # Run Ragas metrics with Ollama judge
        result = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=judge_llm,
            embeddings=judge_embeddings
        )
        
        # Extract scores
        scores = {
            'faithfulness': float(result['faithfulness']),
            'answer_relevance': float(result['answer_relevancy']),
            'context_relevance': float(result['context_precision'])
        }
        
        return scores
    
    def apply_thresholds(self, scores: dict) -> dict:
        """Apply pass/fail thresholds to scores."""
        return {
            metric: 'pass' if score >= self.thresholds[metric] else 'fail'
            for metric, score in scores.items()
        }
    
    def needs_human_review(self, scores: dict) -> bool:
        """Determine if answer should be flagged for human review."""
        return scores['faithfulness'] < self.thresholds['faithfulness']
