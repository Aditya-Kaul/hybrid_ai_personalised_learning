import asyncio
from typing import List, Dict, Any
from backend.app.services.litellm_base import LiteLLMManager
from backend.app.services.rag_engine import RAGEngine
from sentence_transformers import CrossEncoder

class ChatService:
    def __init__(self):
        self.llm_manager = LiteLLMManager()
        self.rag_engine = RAGEngine()
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    async def process_query(self, query: str, chat_history: List[Dict[str, str]]) -> str:
        transformed_query = await self._transform_query(query, chat_history)
        initial_results = await self.rag_engine.search(transformed_query, top_k=10)
        reranked_results = self._rerank_results(transformed_query, initial_results)
        response = await self._generate_response(query, reranked_results, chat_history)
        return response

    async def _transform_query(self, query: str, chat_history: List[Dict[str, str]]) -> str:
        # Update this method to handle chat history without 'role' key
        history_context = "\n".join([f"{msg.get('role', 'user')}: {msg['content']}" for msg in chat_history[-5:]])

        prompt = f"""Given the following chat history and the current query, generate an expanded search query that captures the context and intent of the conversation:

Chat History:
{history_context}

Current Query: {query}

Expanded Search Query:"""

        response = await self.llm_manager.completion_with_retries(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100000
        )

        return response.choices[0].message.content.strip()

    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pairs = [(query, result['summary'] + " " + result['context']) for result in results]
        scores = self.reranker.predict(pairs)
        scored_results = [(result, score) for result, score in zip(results, scores)]
        reranked_results = sorted(scored_results, key=lambda x: x[1], reverse=True)
        return [result for result, _ in reranked_results]

    async def _generate_response(self, query: str, reranked_results: List[Dict[str, Any]], chat_history: List[Dict[str, str]]) -> str:
        context = "\n".join([f"Concept: {result['concept']}\nSummary: {result['summary']}\nContext: {result['context']}" for result in reranked_results[:3]])
        
        # Update this part to handle chat history without 'role' key
        history_context = "\n".join([f"{msg.get('role', 'user')}: {msg['content']}" for msg in chat_history[-5:]])

        prompt = f"""Given the following chat history, context, and the current query, generate a helpful and informative response:

Chat History:
{history_context}

Context:
{context}

Current Query: {query}

Response:"""

        response = await self.llm_manager.completion_with_retries(
           
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100000
        )

        return response.choices[0].message.content.strip()

    def chat(self, query: str, chat_history: List[Dict[str, str]]) -> str:
        return asyncio.run(self.process_query(query, chat_history))

# Example usage
if __name__ == "__main__":
    chat_service = ChatService()
    
    # Simulated chat history
    chat_history = [
        {"content": "What can you tell me about quantum computing?"},
        {"content": "Quantum computing is a type of computation that harnesses the unique properties of quantum mechanics..."},
        {"content": "That's interesting. How does it compare to classical computing?"}
    ]
    
    # New query
    query = "What are some potential applications of quantum computing?"
    
    response = chat_service.chat(query, chat_history)
    print(f"User: {query}")
    print(f"Assistant: {response}")