import os
import pymupdf4llm
import pathlib
from litellm import completion
from langchain.text_splitter import MarkdownTextSplitter

def chunk_pdf(file_path, out_path):
    """
    Chunks a PDF file into smaller segments
    """
    md_text = pymupdf4llm.to_markdown(file_path)
    pathlib.Path(f"{out_path}/output.md").write_bytes(md_text.encode())
    splitter = MarkdownTextSplitter(chunk_size=40, chunk_overlap=0)
    splitter.create_documents([md_text])
    
    return 0

chunk_pdf(file_path="/home/tso/hybrid_ai_personalised_learning/v1/backend/core/pdf_pipeline/input.pdf",out_path="v1/backend/core/pdf_pipeline")
