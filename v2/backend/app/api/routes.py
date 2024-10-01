from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

import asyncio
import os
from dotenv import load_dotenv
import traceback
import logging
import io


# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the .env file
dotenv_path = '/home/tso/hybrid_ai_personalised_learning/v2/backend/.env'
# dotenv_path = '/Users/adityakoul/Desktop/hybrid_ai_personalised_learning/v2/backend/.env'
# Load environment variables from the specified path
load_dotenv(dotenv_path)

# Import your local modules
from backend.app.services.pdf_process import PDFProcessor
from backend.app.services.rag_engine import RAGEngine
from backend.app.services.lesson import LessonGenerator
from backend.app.services.quiz import QuizGenerator
from backend.app.services.chat import ChatService

# Import LiteLLM configuration
from backend.app.services.litellm_base import LiteLLMManager

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize LiteLLM manager
litellm_manager = LiteLLMManager()

# Initialize services with LiteLLM manager
pdf_processor = PDFProcessor()
rag_engine = RAGEngine()
lesson_generator = LessonGenerator()
quiz_generator = QuizGenerator()
chat_service = ChatService()

class ChatRequest(BaseModel):
    query: str
    chat_history: List[Dict[str, str]]

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if file.filename.split(".")[-1].lower() != "pdf":
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        contents = await file.read()
        logger.info(f"PDF file read, size: {len(contents)} bytes")
        
        chunks = await pdf_processor.process_pdf(contents)
        logger.info(f"PDF processed into {len(chunks)} chunks")
        
        if not chunks:
            raise ValueError("No text could be extracted from the PDF")
        
        key_concepts = await rag_engine._generate_key_concepts(chunks)
        await rag_engine.process_chunks(key_concepts,chunks)
        logger.info(f"Generated {len(key_concepts)} key concepts")
        
        return {"message": "PDF processed successfully", "key_concepts": key_concepts}
    except ValueError as ve:
        logger.error(f"Value error in PDF processing: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except IndexError as ie:
        logger.error(f"Index error in PDF processing: {str(ie)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF content: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in PDF processing: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing the PDF: {str(e)}")

@app.post("/test-upload-pdf")
async def test_upload_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        return {"message": f"File {file.filename} received successfully. Size: {len(contents)} bytes"}
    except Exception as e:
        logger.error(f"Error in test upload: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/generate-roadmap")
async def generate_roadmap(key_concepts: List[str]):
    # This is a placeholder. You might want to implement a more sophisticated
    # roadmap generation logic based on the key concepts.
    return {"roadmap": key_concepts}

@app.get("/generate-lesson/{key_concept}")
async def generate_lesson(key_concept: str, vocabulary: str = "mid"):
    lesson = await lesson_generator.generate_lesson(key_concept, vocabulary)
    return {"lesson": lesson}

@app.get("/generate-quiz/{key_concept}")
async def generate_quiz(key_concept: str, num_questions: int = 5):
    quiz = await quiz_generator.generate_quiz(key_concept, num_questions)
    return quiz

@app.post("/chat")
async def chat(request: ChatRequest):
    response = await chat_service.process_query(request.query, request.chat_history)
    return {"response": response}

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG Application API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)