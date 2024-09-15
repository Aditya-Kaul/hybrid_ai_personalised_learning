import os
import sys
from dotenv import load_dotenv
import argparse
from typing import List, Dict, Any
from litellm import completion
import requests

from langchain.prompts import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain.chains import LLMChain
from langchain.schema.language_model import BaseLanguageModel
from langchain_core.pydantic_v1 import BaseModel, Field

# Load environment variables from a .env file
load_dotenv()

# Set the OpenAI API key environment variable (for fallback)
#os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

def get_embedding(text: str) -> List[float]:
    """Get embedding using Ollama's local embedding model."""
    response = requests.post('http://localhost:11434/api/embeddings', 
                             json={'model': 'snowflake-arctic-embed', 'prompt': text})
    return response.json()['embedding']

class LocalLLM(BaseLanguageModel):
    """Custom LLM class to use LiteLLM with Langchain."""
    
    def __call__(self, prompt: str, stop: List[str] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = completion(model="ollama/llama3.1", messages=messages, stop=stop)
        return response.choices[0].message.content

    def _generate_prompt(self, prompt: PromptValue, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> LLMResult:
        text = prompt.to_string()
        result = self._call(text, stop=stop)
        return LLMResult(generations=[[{"text": result}]])

    async def _agenerate_prompt(self, prompt: PromptValue, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> LLMResult:
        raise NotImplementedError("Async generation not implemented for LocalLLM")

    def _stream(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        raise NotImplementedError("Streaming not implemented for LocalLLM")

    def predict(self, text: str, *, stop: Optional[List[str]] = None) -> str:
        return self._call(text, stop=stop)

    def predict_messages(self, messages: List[Dict[str, str]], *, stop: Optional[List[str]] = None) -> str:
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        return self._call(prompt, stop=stop)

    async def apredict(self, text: str, *, stop: Optional[List[str]] = None) -> str:
        raise NotImplementedError("Async prediction not implemented for LocalLLM")

    async def apredict_messages(self, messages: List[Dict[str, str]], *, stop: Optional[List[str]] = None) -> str:
        raise NotImplementedError("Async message prediction not implemented for LocalLLM")


class PersonalizedLearningPath(BaseModel):
    chapters: List[str] = Field(description="List of chapters to learn in order")
    rationale: str = Field(description="Explanation for the suggested learning path")

class AdaptiveQuiz(BaseModel):
    questions: List[Dict[str, Any]] = Field(description="List of quiz questions with options and correct answers")
    difficulty: str = Field(description="Difficulty level of the quiz")

class AdaptiveLearningRAG:
    def __init__(self, texts: List[str]):
        self.llm = LocalLLM()
        self.text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.documents = self.text_splitter.create_documents(texts)
        self.db = FAISS.from_documents(self.documents, get_embedding)

        self.learning_path_prompt = PromptTemplate(
            input_variables=["chapters", "user_name", "knowledge_level"],
            template="Given the following chapters: {chapters}\nGenerate a personalized learning path for {user_name} with a knowledge level of {knowledge_level}. Provide a list of chapters to learn in order and explain the rationale."
        )
        self.learning_path_chain = LLMChain(llm=self.llm, prompt=self.learning_path_prompt, output_key="learning_path")

        self.quiz_prompt = PromptTemplate(
            input_variables=["chapters", "difficulty"],
            template="Create a quiz with 5 questions of {difficulty} difficulty based on the following chapters: {chapters}. For each question, provide 4 options and indicate the correct answer."
        )
        self.quiz_chain = LLMChain(llm=self.llm, prompt=self.quiz_prompt, output_key="quiz")

    def generate_learning_path(self, user_name: str, knowledge_level: str) -> PersonalizedLearningPath:
        chapters = self.extract_chapters()
        result = self.learning_path_chain({"chapters": ", ".join(chapters), "user_name": user_name, "knowledge_level": knowledge_level})
        return PersonalizedLearningPath.parse_raw(result["learning_path"])

    def generate_quiz(self, difficulty: str) -> AdaptiveQuiz:
        chapters = self.extract_chapters()
        result = self.quiz_chain({"chapters": ", ".join(chapters), "difficulty": difficulty})
        return AdaptiveQuiz.parse_raw(result["quiz"])

    def extract_chapters(self) -> List[str]:
        chapters = []
        for doc in self.documents:
            if doc.page_content.strip().lower().startswith("chapter"):
                chapters.append(doc.page_content.strip().split("\n")[0])
        return chapters

def main(document_path: str, user_name: str, knowledge_level: str):
    with open(document_path, 'r') as file:
        text = file.read()

    rag_system = AdaptiveLearningRAG([text])

    # Generate personalized learning path
    learning_path = rag_system.generate_learning_path(user_name, knowledge_level)
    print(f"Personalized Learning Path for {user_name}:")
    for i, chapter in enumerate(learning_path.chapters, 1):
        print(f"{i}. {chapter}")
    print(f"\nRationale: {learning_path.rationale}\n")

    # Generate adaptive quizzes
    difficulties = ["easy", "medium", "hard"]
    for difficulty in difficulties:
        if difficulty == "easy" and knowledge_level != "beginner":
            continue
        if difficulty == "hard" and knowledge_level == "beginner":
            continue

        quiz = rag_system.generate_quiz(difficulty)
        print(f"\n{difficulty.capitalize()} Quiz:")
        for i, question in enumerate(quiz.questions, 1):
            print(f"\nQ{i}: {question['question']}")
            for j, option in enumerate(question['options'], 1):
                print(f"  {j}. {option}")
            print(f"Correct Answer: {question['correct_answer']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a personalized learning path and adaptive quizzes.")
    parser.add_argument("document_path", help="Path to the document file")
    parser.add_argument("user_name", help="Name of the user")
    parser.add_argument("knowledge_level", choices=["beginner", "intermediate", "advanced"], help="User's current knowledge level")
    
    args = parser.parse_args()
    
    main(args.document_path, args.user_name, args.knowledge_level)