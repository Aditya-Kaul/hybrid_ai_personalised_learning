"""
extract_knowledge.py

This module provides functionalities for content analysis and summarization, including:

- Content classification: Classifies text based on difficulty.
- Key concept identification: Identifies and extracts key concepts from the content.
- Summarization:
    - Sub-summary generation: Creates summaries for smaller sections of the content.
    - Top-level summary creation: Generates a comprehensive summary of the entire content.
- Hierarchical index building: Builds a hierarchical index to represent the structure and organization of the content.
- Compression template generation: Creates templates for compressing the content while preserving essential information.
"""
import json
import litellm
import asyncio
from typing import List, Dict, Any
import spacy
from langchain.text_splitter import MarkdownTextSplitter
import pymupdf4llm

# Configure LiteLLM
litellm.set_verbose = True

def paragraphs(doc):
    start = 0
    for token in doc:
        if token.is_space and token.text.count("\n") > 1:
            yield doc[start:token.i]
            start = token.i
    yield doc[start:]

def chunk_pdf(file_path: str, chunk_size: int = 125, chunk_overlap: int = 10) -> List[str]:
    md_text = pymupdf4llm.to_markdown(file_path)
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(md_text)
    paragraphs_list = list(paragraphs(doc))
    paragraphs_text = [para.text for para in paragraphs_list]

    splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.create_documents(paragraphs_text)
    return [chunk.page_content for chunk in chunks]

class HierarchicalIndexAdvanced:
    def __init__(self, file_path: str, chunk_size: int = 125, chunk_overlap: int = 10):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks = []
        self.key_concepts = []
        self.sub_summaries = []
        self.top_level_summary = ""
        self.hierarchical_structure = {}

    async def process_document(self):
        self.chunks = chunk_pdf(self.file_path, self.chunk_size, self.chunk_overlap)

    async def identify_key_concepts(self):
        full_text = ' '.join(self.chunks)
        prompt = f"Identify the top 10 key concepts from the following text. Provide only a comma-separated list of these concepts.\n\nText:\n{full_text[:4000]}"  # Limit to first 4000 chars to avoid token limits
        response = await litellm.acompletion(
            model="mistral/mistral-medium",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        self.key_concepts = [concept.strip() for concept in response.choices[0].message.content.split(',')]

    async def generate_sub_summary(self, chunk_group: str) -> str:
        prompt = f"Provide a concise summary (2-3 sentences) of the following text:\n\n{chunk_group}"
        response = await litellm.acompletion(
            model="gemini/gemini-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()

    async def generate_sub_summaries(self):
        # Group chunks for sub-summaries (e.g., every 5 chunks)
        chunk_groups = [' '.join(self.chunks[i:i+5]) for i in range(0, len(self.chunks), 5)]
        self.sub_summaries = await asyncio.gather(
            *[self.generate_sub_summary(group) for group in chunk_groups]
        )

    async def generate_top_level_summary(self):
        full_text = ' '.join(self.chunks)
        prompt = f"Provide a comprehensive summary (3-4 sentences) of the following text:\n\n{full_text[:4000]}"  # Limit to first 4000 chars
        response = await litellm.acompletion(
            model="gemini/gemini-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        self.top_level_summary = response.choices[0].message.content.strip()

    async def build_hierarchical_index(self):
        await self.process_document()
        await asyncio.gather(
            self.identify_key_concepts(),
            self.generate_sub_summaries(),
            self.generate_top_level_summary()
        )
        
        self.hierarchical_structure = {
            "key_concepts": {
                concept: {
                    "top_level_summary": self.top_level_summary,
                    "sub_summaries": self.sub_summaries,
                    "leaf_nodes": self.chunks
                } for concept in self.key_concepts
            },
            "chunks": {
                f"Chunk_{i}": {
                    "content": chunk,
                    "sub_summary": self.sub_summaries[i // 5] if i // 5 < len(self.sub_summaries) else None
                } for i, chunk in enumerate(self.chunks)
            }
        }

    def get_hierarchical_index(self) -> Dict[str, Any]:
        return self.hierarchical_structure

async def main():
    file_path = "v1/backend/core/pdf_pipeline/input.pdf"  # Replace with your PDF file path
    index = HierarchicalIndexAdvanced(file_path)
    await index.build_hierarchical_index()

    result = index.get_hierarchical_index()

    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

