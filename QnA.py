import os
from langchain_community.document_loaders import PyPDFLoader

from langchain_openai import OpenAI as LangChainOpenAI
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFDirectoryLoader

# from langchain.vectorstores import Chroma 
from langchain_community.vectorstores import Chroma
from config import lessons_collection, textbook_collection

import random
import mesop as me
import mesop.labs as mel

# api_key = os.getenv("OPENAI_API_KEY")

api_key = 'sk-None-1zYnoVmTO81ceVbXneJsT3BlbkFJJDp96o6aEMJCseYIaI0V'
os.environ["OPENAI_API_KEY"] = api_key  

# DATA_FOLDER = '/Users/adityakoul/Documents/ml kb/ML concept notes'
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


def qa_chain_model(chunk_size: int = 1500, chunk_overlap: int = 150) -> RetrievalQA:
    docs = pdf_loader()
    if not docs:
        raise ValueError("No documents were loaded. Please check the PDF file and path.")
    
    generated_lessons = lessons_collection.get()
    lesson_docs = [Document(page_content=doc, metadata={"source": "generated_lesson", **metadata}) 
                   for doc, metadata in zip(generated_lessons['documents'], generated_lessons['metadatas'])]
    # Load textbook chunks
    textbook_chunks = textbook_collection.get()
    textbook_docs = [Document(page_content=doc, metadata=metadata) 
                     for doc, metadata in zip(textbook_chunks['documents'], textbook_chunks['metadatas'])]
    
    # Combine documents, prioritizing generated lessons
    all_docs = lesson_docs + textbook_docs

    embeddings = OpenAIEmbeddings(api_key=api_key)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(all_docs)
    vectorstore = get_or_create_vectorstore(splits, embeddings)
    # vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    llm = ChatOpenAI(model_name="gpt-4o-mini-2024-07-18",temperature=0.7, max_tokens=1000,api_key=os.getenv("OPENAI_API_KEY"))
    retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                template="""
                    You are an AI tutor assisting with questions about specific machine learning lessons.
                    Use the following pieces of context to answer the question at the end.
                    Prioritize information from the generated lesson content if available.
                    If you don't know the answer based on the given context, 
                    say that you don't know and suggest asking for clarification about the specific lesson topic.
                    {context}
                    
                Question: {question}
                Detailed Answer:""",
                input_variables=["context", "question"]
            )
        }
    )
qa_chain = qa_chain_model()

def transform(prompt: str) -> str:
    result = qa_chain({'query': prompt, 'include_run_info': True})
    text_response = result['result']
    # Check if the response is based on generated lesson content
    source_docs = result.get('source_documents', [])
    is_from_lesson = any('generated_lesson' in doc.metadata.get('source', '') for doc in source_docs)
    
    # if is_from_lesson and exp_checks(prompt):
    #     enhanced_response = post_process_answer(prompt, text_response)
    # else:
    #     enhanced_response = text_response
    enhanced_response = text_response
    return enhanced_response

# def exp_checks(question):
#     visual_keywords = ['detail', 'briefly', 'detailed','complete', 'elaborate', 'full']
#     return any( keyword in question.lower() for keyword in visual_keywords)

# def post_process_answer(question, answer):
#     enhanced_text_prompt = f"Enhance the following answer with a step-by-step explanation:\n\nQuestion: {question}\n\nAnswer: {answer}"
#     detailed_explanation = generate_detailed_explanation(enhanced_text_prompt)
#     return f"{answer}\n\n{detailed_explanation}"

# def generate_detailed_explanation(prompt):
#     # client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#     client = OpenAI(api_key=api_key)
#     response = client.chat.completions.create(
#         model="gpt-4o-mini-2024-07-18",
#         messages=[
#             {"role": "system", "content": "You are an AI assistant that provides detailed explanations for complex concepts."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=2000
#     )
#     return response.choices[0].message.content


#=========================================================================<<>>

# import random
# import mesop as me
# import mesop.labs as mel

# me.colab_run()

# @me.page(path="/chat")
# def chat():
#     mel.chat(transform)