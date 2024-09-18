"""
python -m spacy download en_core_web_trf

"""

import os
import pymupdf4llm
import pathlib
from litellm import completion
from langchain.text_splitter import MarkdownTextSplitter
import spacy



def paragraphs(doc):
    start = 0
    for token in doc:
        if token.is_space and token.text.count("\n") > 1:
            yield doc[start:token.i]
            start = token.i
    yield doc[start:]


def chunk_pdf(file_path, out_path):
    """
    Chunks a PDF file into smaller segments
    """
    md_text = pymupdf4llm.to_markdown(file_path)
    pathlib.Path(f"{out_path}/output.md").write_bytes(md_text.encode())
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(md_text)
    paragraphs_list = list(paragraphs(doc)) 

    # Convert spaCy spans to strings
    paragraphs_text = [para.text for para in paragraphs_list]
    
    # Use MarkdownTextSplitter for further chunking if needed
    splitter = MarkdownTextSplitter(chunk_size=20, chunk_overlap=10)
    chunks = splitter.create_documents(paragraphs_text)
    
    """
    This saves the chunks as Markdown files. We need to change it to store in lancedb eventually
    """
    for i, para in enumerate(paragraphs_list):
        # Check if paras are correct
        if i==0 | i==21:
            pathlib.Path(f"{out_path}/paragraph_{i}.md").write_text(para.text, encoding='utf-8')
    
    return len(paragraphs_list)
    



result = chunk_pdf(file_path="/home/tso/hybrid_ai_personalised_learning/v1/backend/core/pdf_pipeline/input.pdf",
                   out_path="v1/backend/core/pdf_pipeline")
print(f"Created {result} chunks.")
