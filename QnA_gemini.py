import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import Chroma
from new_config import get_generated_lesson
import streamlit as st
import google.generativeai as genai

# Set up Google API key
api_key = 'AIzaSyDjs6-jQNsmYFcqK54Mk5zsPDIBwJlk29E'
GOOGLE_API_KEY = api_key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
genai.configure(api_key=GOOGLE_API_KEY)

DATA_FOLDER = '/Users/adityakoul/Documents/ml kb/Text Book'

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
    print(module['module_name'], lesson['name'])

    # Testing 
    # module = 'Classification'
    # lesson = 'Training a Binary Classifier'
    # lesson_content = get_generated_lesson(module, lesson)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++

    lesson_content = get_generated_lesson(module['module_name'], lesson['name'],st.session_state.email)
    lesson_doc = Document(page_content=lesson_content['documents'][0], metadata={"source": "current_lesson"})
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vectorstore = Chroma.from_documents(documents=[lesson_doc], embedding=embeddings)
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

def qa_chain_model(chunk_size: int = 1500, chunk_overlap: int = 150) -> RetrievalQA:
    docs = pdf_loader()
    if not docs:
        raise ValueError("No documents were loaded. Please check the PDF file and path.")

    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, max_output_tokens=1000)

    retriever = get_lesson_specific_retriever()
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                template="""
                    You are an AI tutor assisting with questions on the current machine learning lesson
                    from the book 'Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow' by Aurélien Géron.
                    Use the following pieces of context to answer the question at the end.
                    Prioritize information from the generated lesson content if available.
                    If the question asks for more details about "this lesson", provide information specifically about the detailed summary of context. 
                    If you don't know the answer based on the given context, 
                    say that you don't know and suggest asking for clarification about the specific lesson topic.
                    {context}
                    
                Question: {question}
                Detailed Answer:""",
                input_variables=["context", "question"]
            )
        }
    )

def transform(prompt: str) -> str:
    qa_chain = qa_chain_model()
    result = qa_chain({'query': prompt, 'include_run_info': True})
    text_response = result['result']
    source_docs = result.get('source_documents', [])
    is_from_lesson = any('generated_lesson' in doc.metadata.get('source', '') for doc in source_docs)
    
    enhanced_response = text_response
    return enhanced_response

# Example usage