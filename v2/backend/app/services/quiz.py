import asyncio
from typing import List, Dict
from backend.app.services.rag_engine import RAGEngine
from backend.app.services.litellm_base import LiteLLMManager

class QuizGenerator:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.llm_manager = LiteLLMManager()

    async def generate_quiz(self, key_concept: str, num_questions: int = 5) -> Dict[str, List[Dict[str, str]]]:
        # Perform retrieval on key concept
        search_results = await self.rag_engine.search(key_concept, top_k=3)

        # Prepare context from search results
        context = "\n".join([f"Concept: {result['concept']}\nSummary: {result['summary']}\nContext: {result['context']}" for result in search_results])

        # Generate the quiz
        prompt = f"""Generate a quiz on the key concept: "{key_concept}".
        Use the following context to inform your questions:

        {context}

        Please create {num_questions} multiple-choice questions. Each question should have 4 options (A, B, C, D) with only one correct answer.

        Format your response as follows for each question:

        Question: [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]
        Correct Answer: [A/B/C/D]
        Explanation: [Brief explanation of the correct answer]

        Ensure that the questions cover different aspects of the key concept and vary in difficulty."""

        response = await self.llm_manager.completion_with_retries(
            
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100000
        )

        # Parse the response into a structured quiz format
        raw_quiz = response.choices[0].message.content
        questions = raw_quiz.split("\n\n")
        
        structured_quiz = []
        for q in questions:
            lines = q.split("\n")
            question = {
                "question": lines[0].replace("Question: ", ""),
                "options": {
                    "A": lines[1].replace("A) ", ""),
                    "B": lines[2].replace("B) ", ""),
                    "C": lines[3].replace("C) ", ""),
                    "D": lines[4].replace("D) ", "")
                },
                "correct_answer": lines[5].replace("Correct Answer: ", ""),
                "explanation": lines[6].replace("Explanation: ", "")
            }
            structured_quiz.append(question)

        return {"questions": structured_quiz}

    def generate_quiz_sync(self, key_concept: str, num_questions: int = 5) -> Dict[str, List[Dict[str, str]]]:
        return asyncio.run(self.generate_quiz(key_concept, num_questions))


# Example usage
if __name__ == "__main__":
    quiz_gen = QuizGenerator()
    quiz = quiz_gen.generate_quiz_sync("Quantum Computing", 5)
    
    print("Generated Quiz:")
    for i, q in enumerate(quiz["questions"], 1):
        print(f"\nQuestion {i}: {q['question']}")
        for option, text in q['options'].items():
            print(f"{option}) {text}")
        print(f"Correct Answer: {q['correct_answer']}")
        print(f"Explanation: {q['explanation']}")