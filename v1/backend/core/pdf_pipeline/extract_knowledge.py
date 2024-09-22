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
import os
import spacy
import litellm
import asyncio
import pymupdf4llm

from typing import List, Dict, Any

from langchain.text_splitter import MarkdownTextSplitter

from litellm import RateLimitError

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

    splitter = MarkdownTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
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
        self.retry_delay = 1  # Start with 1 second delay
        self.token_usage = {}


    async def process_document(self):
        self.chunks = chunk_pdf(
            self.file_path, self.chunk_size, self.chunk_overlap)

    async def litellm_completion_with_retries(self, model: str, messages: List[Dict[str, str]], max_tokens: int, max_retries: int = 5):
        for attempt in range(max_retries):
            try:
                response = await litellm.acompletion(model=model, messages=messages, max_tokens=max_tokens)
                
                # Update token usage
                if model not in self.token_usage:
                    self.token_usage[model] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                
                self.token_usage[model]["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage[model]["completion_tokens"] += response.usage.completion_tokens
                self.token_usage[model]["total_tokens"] += response.usage.total_tokens
                
                return response
            except litellm.RateLimitError as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    self.retry_delay *= 2  # Exponential backoff
                else:
                    raise e
            except Exception as e:
                print(f"Unexpected error: {e}")
                raise e

    async def identify_key_concepts(self):
        #full_text = ' '.join(self.chunks)
        # Limit to first 4000 chars to avoid token limits
        for chunk in self.chunks:
            prompt = f"Identify the top 2 key concepts from the following text. Provide only a comma-separated list of these concepts.\n\nText:\n{chunk}"
            response = await self.litellm_completion_with_retries(
                model="mistral/mistral-medium",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192
            )
            self.key_concepts = [
                concept.strip() for concept in response.choices[0].message.content.split(',')]

    async def generate_sub_summary(self, chunk_group: str) -> str:
        prompt = f"Provide a concise summary (2-3 sentences) of the following text:\n\n{chunk_group}"
        response = await self.litellm_completion_with_retries(
            model="gemini/gemini-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )
        return response.choices[0].message.content.strip()

    async def generate_sub_summaries(self):
        chunk_groups = [' '.join(self.chunks[i:i+5])
                        for i in range(0, len(self.chunks), 5)]
        self.sub_summaries = []
        for group in chunk_groups:
            summary = await self.generate_sub_summary(group)
            self.sub_summaries.append(summary)
            # Add a delay between requests to respect rate limits
            await asyncio.sleep(1.5)

    async def generate_top_level_summary(self):
        full_text = ' '.join(self.chunks)
        # Limit to first 4000 chars
        prompt = f"Provide a comprehensive summary (3-4 sentences) of the following text:\n\n{full_text[:4000]}"
        response = await self.litellm_completion_with_retries(
            model="gemini/gemini-pro",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8192
        )
        self.top_level_summary = response.choices[0].message.content.strip()

    async def build_hierarchical_index(self):
        await self.process_document()
        await self.identify_key_concepts()
        await self.generate_sub_summaries()
        await self.generate_top_level_summary()

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
            },
            "token_usage": self.token_usage
        }

    def get_hierarchical_index(self) -> Dict[str, Any]:
        return self.hierarchical_structure

    def save_hierarchical_index(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.hierarchical_structure, f,
                      ensure_ascii=False, indent=2)
        print(f"Hierarchical index saved to {output_path}")


async def main():
    # Replace with your PDF file path
    file_path = "v1/backend/core/pdf_pipeline/input.pdf"
    output_path = "v1/backend/core/pdf_pipeline/output.json"
    index = HierarchicalIndexAdvanced(file_path)
    # Check if  Directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        await index.build_hierarchical_index()
        index.save_hierarchical_index(output_path)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
