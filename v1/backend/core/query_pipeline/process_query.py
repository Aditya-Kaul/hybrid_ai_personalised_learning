"""
Query classification using reranking
Query transform
Generate Lesson
Generate Quiz
Generate QnA
"""

import json
from typing import List, Dict, Any
import random
import asyncio
from rerankers import Reranker
from transformers import pipeline, AutoTokenizer
import torch
import litellm
import re

class RAGKnowledgeProcessor:
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r') as file:
            self.data = json.load(file)
        self.reranker = Reranker('cross-encoder')
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        self.qa_model = pipeline("text2text-generation", model="valhalla/t5-base-qa-qg-hl")
        self.tokenizer = AutoTokenizer.from_pretrained("valhalla/t5-base-qa-qg-hl")
        self.retry_delay = 1
        self.token_usage = {}

    async def litellm_completion_with_retries(self, model: str, messages: List[Dict[str, str]], max_tokens: int, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                response = await litellm.acompletion(model=model, messages=messages, max_tokens=max_tokens)
                
                # Update token usage
                if model not in self.token_usage:
                    self.token_usage[model] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                
                self.token_usage[model]["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage[model]["completion_tokens"] += response.usage.completion_tokens
                self.token_usage[model]["total_tokens"] += response.usage.total_tokens
                
                return response
            except litellm.RateLimitError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    raise e
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise e
    


    def classify_query(self, query: str) -> str:
        key_concepts = list(self.data['key_concepts'].keys())
        results = self.reranker.rank(query=query, docs=key_concepts)
        return results.top_k(1)[0].text

    def transform_query(self, query: str) -> str:
        input_length = len(self.summarizer.tokenizer.tokenize(query))
        max_length = min(50, input_length + 10)  # Adjust max_length based on input
        return self.summarizer(query, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']

    async def generate_lesson(self, concept: str) -> Dict[str, Any]:
        concept_data = self.data['key_concepts'][concept]
        
        # Prepare the content for the lesson
        lesson_content = f"Key Concept: {concept}\n\n"
        lesson_content += f"Summary: {concept_data['top_level_summary']}\n\n"
        lesson_content += "Sub-concepts and Details:\n"
        for i, sub_summary in enumerate(concept_data["sub_summaries"], 1):
            lesson_content += f"{i}. {sub_summary}\n"
        lesson_content += "\nAdditional Information:\n"
        for leaf_node in concept_data["leaf_nodes"]:
            lesson_content += f"- {leaf_node}\n"

        # Generate the lesson using litellm
        prompt = f"Based on the following information, generate a comprehensive 1500-word lesson about {concept}:\n\n{lesson_content}\n\nLesson:"
        
        response = await self.litellm_completion_with_retries(
            model="gemini/gemini-pro", 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192  # Adjust as needed to get approximately 1500 words
        )

        generated_lesson = response.choices[0].message.content.strip()

        return {
            "concept": concept,
            "lesson_text": generated_lesson,
            "original_content": lesson_content
        }

    
    async def generate_questions(self, context: str, num_questions: int = 5) -> List[Dict[str, str]]:
        prompt = f"""Generate {num_questions} question-answer pairs based on the following context. 
        Format each pair as 'Question: [question] Answer: [answer]'.

        Context: {context}

        Question-Answer Pairs:
        """

        response = await self.litellm_completion_with_retries(
            model="gemini/gemini-pro",  # You can change this to your preferred model
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )

        generated_text = response.choices[0].message.content.strip()

        questions = []
        # Use regex to find question-answer pairs
        pairs = re.findall(r'Question:\s*(.*?)\s*Answer:\s*(.*?)(?=(?:\n\s*Question:|$))', generated_text, re.DOTALL)
        
        for question, answer in pairs:
            questions.append({
                "question": question.strip(),
                "answer": answer.strip()
            })

        return questions

    async def generate_quiz(self, lesson: Dict[str, Any]) -> List[Dict[str, str]]:
        return await self.generate_questions(lesson['lesson_text'])

    async def generate_qna(self, lesson: Dict[str, Any]) -> List[Dict[str, str]]:
        return await self.generate_questions(lesson['lesson_text'])

    async def process_query(self, query: str) -> Dict[str, Any]:
        classified_concept = self.classify_query(query)
        transformed_query = self.transform_query(query)
        lesson = await self.generate_lesson(classified_concept)
        quiz = await self.generate_quiz(lesson)
        qna = await self.generate_qna(lesson)

        return {
            "original_query": query,
            "classified_concept": classified_concept,
            "transformed_query": transformed_query,
            "lesson": lesson,
            "quiz": quiz,
            "qna": qna,
            "token_usage": self.token_usage
        }

# Usage example
async def main():
    processor = RAGKnowledgeProcessor('/home/tso/hybrid_ai_personalised_learning/v1/backend/core/pdf_pipeline/output.json')
    result = await processor.process_query("What is clustering in machine learning?")
    output_path = "v1/backend/core/query_pipeline/r_output.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f,
                      ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())