import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from new_config import get_generated_lesson, get_student_details
import streamlit as st
import google.generativeai as genai
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up Google API key
api_key = 'AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E'
GOOGLE_API_KEY = api_key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

DATA_FOLDER = '/Users/adityakoul/Documents/ml kb/Text Book'

class ConversationHistory:
    def __init__(self, max_history: int = 5):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history

    def add_interaction(self, question: str, answer: str):
        self.history.append({"question": question, "answer": answer})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self) -> str:
        return "\n".join([f"Q: {interaction['question']}\nA: {interaction['answer']}" for interaction in self.history])

conversation_history = ConversationHistory()

def pdf_loader(data_folder=DATA_FOLDER):
    loader = PyPDFDirectoryLoader(DATA_FOLDER)
    docs = loader.load()
    return docs

def get_or_create_vectorstore(documents, embeddings, persist_directory='./embed_chroma_db'):
    if os.path.exists(persist_directory):
        return Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    return vectorstore

def get_lesson_specific_retriever():
    module = st.session_state.current_module
    lesson = st.session_state.current_lesson
    lesson_content = get_generated_lesson(module['module_name'], lesson['name'], st.session_state.email)
    lesson_doc = Document(page_content=lesson_content['documents'][0], metadata={"source": "current_lesson"})
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = Chroma.from_documents(documents=[lesson_doc], embedding=embeddings)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

def dynamic_summarize(text: str, max_length: int = 500) -> str:
    sentences = text.split('.')
    summary = []
    current_length = 0
    
    for sentence in sentences:
        if current_length + len(sentence) <= max_length:
            summary.append(sentence)
            current_length += len(sentence)
        else:
            break
    
    return '. '.join(summary) + '.'

def calculate_confidence_score(question: str, answer: str, context: str) -> float:
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([question, answer, context])
    
    question_vector = tfidf_matrix[0]
    answer_vector = tfidf_matrix[1]
    context_vector = tfidf_matrix[2]
    
    qa_similarity = cosine_similarity(question_vector, answer_vector)[0][0]
    ac_similarity = cosine_similarity(answer_vector, context_vector)[0][0]
    
    confidence_score = (qa_similarity + ac_similarity) / 2
    return confidence_score

def get_personalized_difficulty(email: str) -> str:
    student_details = get_student_details(email)
    overall_progress = student_details.get('progress', 50)  # Default to 50 if not found
    
    if overall_progress < 30:
        return "beginner"
    elif overall_progress < 70:
        return "intermediate"
    else:
        return "advanced"

def qa_chain_model(chunk_size: int = 1500, chunk_overlap: int = 150) -> RetrievalQA:
    docs = pdf_loader()
    if not docs:
        raise ValueError("No documents were loaded. Please check the PDF file and path.")

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, max_output_tokens=1000)

    retriever = get_lesson_specific_retriever()
    
    prompt_template = """
    You are an AI tutor assisting with questions about the current machine learning lesson.
    The current lesson is about "{lesson_name}" from the module "{module_name}".
    The student's current skill level is: {difficulty_level}

    Use the following context to answer the question:
    {context}

    Recent conversation history:
    {conversation_history}

    If the question asks for more details about "this lesson", provide information specifically about
    the "{lesson_name}" lesson.

    If you don't know the answer based on the given context, say that you don't know and suggest
    asking for clarification about the specific topic within the "{lesson_name}" lesson.

    Current lesson context:
    {lesson_context}

    Question: {question}
    Detailed Answer:
    """

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question", "lesson_name", "module_name", "lesson_context", "conversation_history", "difficulty_level"]
            )
        }
    )

def transform(prompt: str) -> str:
    qa_chain = qa_chain_model()
    
    module = st.session_state.current_module
    lesson = st.session_state.current_lesson
    lesson_content = get_generated_lesson(module['module_name'], lesson['name'], st.session_state.email)
    lesson_context = dynamic_summarize(lesson_content['documents'][0])
    
    difficulty_level = get_personalized_difficulty(st.session_state.email)

    result = qa_chain({
        'query': prompt,
        'lesson_name': lesson['name'],
        'module_name': module['module_name'],
        'lesson_context': lesson_context,
        'conversation_history': conversation_history.get_context(),
        'difficulty_level': difficulty_level,
        'include_run_info': True
    })
    
    text_response = result['result']
    source_docs = result.get('source_documents', [])
    is_from_lesson = any('current_lesson' in doc.metadata.get('source', '') for doc in source_docs)
    
    confidence_score = calculate_confidence_score(prompt, text_response, lesson_context)
    
    if confidence_score < 0.5:
        clarification_prompt = f"I'm not entirely sure about the answer. Could you please clarify if you're asking about:\n1. {lesson['name']}\n2. General machine learning concepts\n3. Something else related to {module['module_name']}?"
        text_response += f"\n\n{clarification_prompt}"
    
    if is_from_lesson:
        text_response += f"\n\nThis information is directly related to the current lesson. (Confidence: {confidence_score:.2f})"
    else:
        text_response += f"\n\nThis information is from the general course material and may not be specific to the current lesson. (Confidence: {confidence_score:.2f})"

    conversation_history.add_interaction(prompt, text_response)

    return text_response