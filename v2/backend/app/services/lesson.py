import asyncio
from typing import List, Dict, Any
from backend.app.services.rag_engine import RAGEngine
from backend.app.services.litellm_base import LiteLLMManager
import logging

logger = logging.getLogger(__name__)

class LessonGenerator:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.llm_manager = LiteLLMManager()

    async def generate_lesson(self, key_concept: str, vocabulary: str = "mid") -> str:
        try:
            # Validate vocabulary level
            if vocabulary not in ["easy", "mid", "hard"]:
                raise ValueError("Vocabulary must be 'easy', 'mid', or 'hard'")

            # Perform retrieval on key concept
            search_results = await self.rag_engine.search(key_concept, top_k=3)

            if not search_results:
                logger.warning(f"No search results found for key concept: {key_concept}")
                context = "No additional context available."
            else:
                # Prepare context from search results
                context = "\n".join([f"Concept: {result['concept']}\nSummary: {result['summary']}\nContext: {result['context']}" for result in search_results])

            # Generate the lesson
            prompt = f"""Generate a comprehensive lesson on the key concept: "{key_concept}".
            Use the following context to inform your lesson:

            {context}

            Please create a self-sufficient article that thoroughly explains this concept. 
            The lesson should be written at a {vocabulary} vocabulary level.

            Structure the lesson as follows:
            1. Introduction: Brief overview of the concept
            2. Main Content: Detailed explanation with examples
            3. Applications: Real-world uses or implications
            4. Summary: Recap of key points

            Ensure the content is engaging, informative, and appropriate for the {vocabulary} vocabulary level."""

            response = await self.llm_manager.completion_with_retries(
                
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100000
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in generate_lesson: {str(e)}")
            raise

    async def generate_lesson_async(self, key_concept: str, vocabulary: str = "mid") -> str:
        return await self.generate_lesson(key_concept, vocabulary)

    def generate_lesson_sync(self, key_concept: str, vocabulary: str = "mid") -> str:
        return asyncio.run(self.generate_lesson(key_concept, vocabulary))


# Example usage
if __name__ == "__main__":
    lesson_gen = LessonGenerator()
    lesson = lesson_gen.generate_lesson_sync("Anomaly Detection", "mid")
    print(lesson)