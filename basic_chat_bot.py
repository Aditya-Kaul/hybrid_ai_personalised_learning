import os
# from langchain.document_loaders import PyPDFLoader #depracated gives warning
from langchain_community.document_loaders import PyPDFLoader
from time import perf_counter

# from langchain.llms import OpenAI #depracated gives warning
# from langchain_community.llms import OpenAI #depracated gives warning
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader  # use it when using text files
from langchain.indexes import VectorstoreIndexCreator
from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings #depracated gives warning
from langchain_openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma # use it when using chromadb

import random
import time
import mesop as me
import mesop.labs as mel

os.environ["OPENAI_API_KEY"] = "api_key"  

# PDF data loading
DATA_FOLDER = 'data/Text Book'
# DATA_FOLDER = '/Users/adityakoul/Library/CloudStorage/OneDrive-UniversityofExeter/TextBook'

def pdf_loader(data_folder=DATA_FOLDER):
    print([fn for fn in os.listdir(DATA_FOLDER) if fn.endswith('.pdf')])
    loaders = [PyPDFLoader(os.path.join(DATA_FOLDER, fn))
               for fn in os.listdir(DATA_FOLDER) if fn.endswith('.pdf')]
    print(f'{len(loaders)} file loaded')
    return loaders


# DATA_FOLDER_TXT = '/Users/adityakoul/Downloads/week_1'
# def txt_loader(data_folder=DATA_FOLDER_TXT):
#     loaders = [TextLoader(os.path.join(data_folder, fn))
#                for fn in os.listdir(data_folder) if fn.endswith('.txt')]
#     return loaders

def qa_model(chunk_size: int = 1000, chunk_overlap: int = 50) -> RetrievalQA:
    embedding = OpenAIEmbeddings()
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    llm = OpenAI(model_name="gpt-3.5-turbo-instruct",temperature=0.9,api_key=os.getenv('OPENAI_API_KEY'),max_tokens=256)
    loaders = pdf_loader()
    # loaders = txt_loader()
    index_creator = VectorstoreIndexCreator(embedding=embedding,text_splitter=splitter)
    index = index_creator.from_loaders(loaders)
    retriever = index.vectorstore.as_retriever(search_type="similarity",search_kwargs={"k": 4})

    return RetrievalQA.from_chain_type(llm=llm,chain_type="stuff",retriever=retriever,return_source_documents=True,
                                       input_key="question")

tick = perf_counter()
qa_chain = qa_model()
print(f'Time span for building index: {perf_counter() - tick}')

me.colab_run()

@me.page(path="/chat")
def chat():
    mel.chat(transform)

def transform(prompt: str, history: list[mel.ChatMessage]) -> str:
    tick = perf_counter()
    # print(f'Time span for building index: {perf_counter() - tick}')
    tick_ = perf_counter()
    result = qa_chain({'question': prompt, 'include_run_info': True})
    print(f'Time span for query: {perf_counter() - tick_}')
    print(result['result'])
    return result['result']


