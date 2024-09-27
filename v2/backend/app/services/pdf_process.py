import spacy
import pymupdf4llm
from typing import List
from langchain.text_splitter import MarkdownTextSplitter

import tempfile
import os


class PDFProcessor:
    def __init__(self, chunk_size: int = 125, chunk_overlap: int = 10):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.nlp = spacy.load("en_core_web_trf")

    def paragraphs(self, doc):
        start = 0
        for token in doc:
            if token.is_space and token.text.count("\n") > 1:
                yield doc[start:token.i]
                start = token.i
        yield doc[start:]

    async def chunk_pdf(self, data: bytes) -> List[str]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(data)
            temp_file_path = temp_file.name

        try:
            md_text = pymupdf4llm.to_markdown(temp_file_path)
            doc = self.nlp(md_text)
            paragraphs_list = list(self.paragraphs(doc))
            paragraphs_text = [para.text for para in paragraphs_list]

            splitter = MarkdownTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            chunks = splitter.create_documents(paragraphs_text)
            return [chunk.page_content for chunk in chunks]
        finally:
            # Clean up the temporary file
            
            os.unlink(temp_file_path)

        

    async def process_pdf(self, data: bytes) -> List[str]:
        # This method combines extraction and chunking
        return await self.chunk_pdf(data)
