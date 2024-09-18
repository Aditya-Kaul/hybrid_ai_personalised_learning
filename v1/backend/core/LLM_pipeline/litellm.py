# litellm api wrapper class for langchanin
import os
from typing import List
import lancedb
from litellm import completion
from sentence_transformers import SentenceTransformer

# Configuration
LANCEDB_URI = "data/lancedb"  # Local LanceDB storage
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformer model
LLM_MODEL = "gemini-1.5-pro-001"  # You can change this to any model supported by LiteLLM

# Initialize embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Initialize LanceDB
db = lancedb.connect(LANCEDB_URI)

def create_embeddings(texts: List[str]) -> List[List[float]]:
    return embedding_model.encode(texts).tolist()

def index_documents(documents: List[dict]):
    table = db.create_table("documents", data=[
        {**doc, "embedding": emb} for doc, emb in zip(documents, create_embeddings([doc["text"] for doc in documents]))
    ])
    return table

def search_documents(query: str, k: int = 5):
    table = db.open_table("documents")
    results = table.search(create_embeddings([query])[0]).limit(k).to_list()
    return results

def generate_response(query: str, context: List[str]):
    prompt = f"Query: {query}\n\nContext:\n" + "\n".join(context)
    print(prompt)
    response = completion(
        model=LLM_MODEL, 
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def rag_query(query: str):
    # Search for relevant documents
    search_results = search_documents(query)
    context = [result["text"] for result in search_results]
    
    # Generate response using LiteLLM
    response = generate_response(query, context)
    return response

def process_pdf(file_path):
    # Read the PDF file
    with open(file_path, 'r') as file:
        text = file.read()
    # Split the text into chunks
    chunks = [text[i:i+100] for i in range(0, len(text), 100)]
    return chunks

# Example usage
if __name__ == "__main__":
    # Sample documents (you would typically load these from a file or database)

    # documents = [
    #     {"id": 1, "text": "LanceDB is a serverless vector database."},
    #     {"id": 2, "text": "LiteLLM is a library for easy interaction with various LLM APIs."},
    #     # Add more documents as needed
    # ]

    documents = process_pdf("/Users/adityakoul/Desktop/hybrid_ai_personalised_learning/v1/backend/core/pdf_pipeline/input.pdf")
    # Index the documents
    index_documents(documents)

    # Example query
    query = "What is design patterns?"
    response = rag_query(query)
    print(f"Query: {query}")
    print(f"Response: {response}")