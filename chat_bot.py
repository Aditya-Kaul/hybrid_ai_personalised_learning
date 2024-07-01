import os
from modules.plots import *

from langchain_community.document_loaders import PyPDFLoader
from time import perf_counter

from langchain_openai import OpenAI as LangChainOpenAI
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# from langchain.vectorstores import Chroma 
from langchain_community.vectorstores import Chroma

import random
import mesop as me
import mesop.labs as mel

os.environ["OPENAI_API_KEY"] = "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"  

# PDF data loading
# DATA_FOLDER = '/Users/adityakoul/Documents/ml kb/ML concept notes'
DATA_FOLDER = '/Users/adityakoul/Documents/ml kb/Text Book'

plot_generators = {
    'kmeans': generate_kmeans_plot,
    'linear regression': generate_linear_regression_plot,
    'decision tree': generate_decision_tree_plot,
    'pca': generate_pca_plot,
    'svm': generate_svm_plot
}

def pdf_loader(data_folder=DATA_FOLDER):
    loader = PyPDFDirectoryLoader(DATA_FOLDER)
    docs = loader.load()
    return docs


def qa_chain_model(chunk_size: int = 1000, chunk_overlap: int = 50) -> RetrievalQA:
    docs = pdf_loader()
    if not docs:
        raise ValueError("No documents were loaded. Please check the PDF file and path.")
    embeddings = OpenAIEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    llm = LangChainOpenAI(model_name="gpt-3.5-turbo-instruct",temperature=0.9,max_tokens=256,api_key=os.getenv('OPENAI_API_KEY'))
    retriever = vectorstore.as_retriever(search_type="similarity",search_kwargs={"k": 4})
    return RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={
        "prompt": PromptTemplate(
            template="""Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            {context}
            Question: {question}
            Detailed Answer:""",
                    input_variables=["context", "question"]
                )
            }
    )
    # return RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=retriever,return_source_documents=True,
    #                                    input_key="question")

# tick = perf_counter()
qa_chain = qa_chain_model()
# print(f'Time span for building index: {perf_counter() - tick}')

me.colab_run()

@me.page(path="/chat")
def chat():
    mel.chat(transform)

# def transform(prompt: str, history: list[mel.ChatMessage]) -> str:
    # tick = perf_counter()
    # # # print(f'Time span for building index: {perf_counter() - tick}')
    # # tick_ = perf_counter()
    # result = qa_chain({'question': prompt, 'include_run_info': True})
    # print(f'Time span for query: {perf_counter() - tick_}')
    # print(result['result'])
    # return result['result']

def transform(prompt: str, history: list[mel.ChatMessage]) -> str:
    result = qa_chain({'query': prompt, 'include_run_info': True})
    text_response = result['result']
    if visual_checks(prompt):
        # image_prompt = f"Create a visual explanation for: {prompt}"
        image_url = generate_image(prompt)
        return f"{text_response}\n\nVisual explanation: {image_url}"
    
    return text_response


def visual_checks(query):
    visual_keywords = ['plot', 'graph', 'diagram', 'visual', 'picture']
    return any( keyword in query.lower() for keyword in visual_keywords)


def generate_image(prompt):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_urls = [image.url for image in response.data]
    return image_urls[0]
