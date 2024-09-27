import asyncio
from typing import List, Dict, Any
import lancedb
import uuid
import itertools
import numpy as np
import uuid
import traceback
import logging
import pyarrow as pa
from backend.app.services.litellm_base import LiteLLMManager
logger = logging.getLogger(__name__)
class RAGEngine:
    def __init__(self, table_name: str = "vectors"):
        self.llm_manager = LiteLLMManager()
        self.vector_store = VectorStore(table_name)

    async def process_chunks(self,key_concepts: str, chunks: List[str]):
        try:
            
            full_text = ' '.join(chunks)
            doc_embedding = await self.llm_manager.get_embedding(full_text)
            
            for concept in key_concepts:
                try:
                    summary, context = await self._generate_summary_and_context(concept, chunks)
                    context_embedding = await self.llm_manager.get_embedding(summary + " " + context)
                    self.vector_store.add(concept, summary, context, doc_embedding, context_embedding)
                except Exception as e:
                    logger.error(f"Error processing concept '{concept}': {str(e)}")
                    logger.error(traceback.format_exc())
        except Exception as e:
            logger.error(f"Error in process_chunks: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def _generate_key_concepts(self, chunks: List[str]) -> List[str]:
        MAX_TOKENS = 128000  # Approximate token limit for 128K context window
        CHARS_PER_TOKEN = 4  # Approximate number of characters per token

        async def process_text_part(text_part: str) -> List[str]:
            prompt = f"Identify the top 3 key concepts from the following text. Provide only a comma-separated list of these concepts.\n\nText:\n{text_part}"
            response = await self.llm_manager.completion_with_retries(
               
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100000
            )
            await asyncio.sleep(1.5)  # Add a small delay to respect rate limits
            return [concept.strip() for concept in response.choices[0].message.content.split(',')]

        full_text = ' '.join(chunks)
        max_chars = MAX_TOKENS * CHARS_PER_TOKEN

        if len(full_text) <= max_chars:
            return await process_text_part(full_text)
        else:
            # Split the text into parts that fit within the context window
            text_parts = [full_text[i:i+max_chars] for i in range(0, len(full_text), max_chars)]
            
            # Process each part and collect the results
            results = await asyncio.gather(*[process_text_part(part) for part in text_parts])
            
            # Flatten the list of lists and remove duplicates while preserving order
            all_concepts = list(dict.fromkeys(itertools.chain(*results)))
            
            # Return the top 10 concepts (or all if less than 10)
            return all_concepts[:10]

    async def _generate_summary_and_context(self, concept: str, chunks: List[str]) -> tuple[str, str]:
        full_text = ' '.join(chunks)
        prompt = f"""Generate a summary and context for the concept "{concept}" based on the following text:

    Text: {full_text[:7000]}

    1. Summary (focus on the concept):
    2. Context (refer to the entire text):

    Provide your response in the following format:
    Summary: [Your summary here]
    Context: [Your context here]"""

        response = await self.llm_manager.completion_with_retries(
          
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100000
        )
        content = response.choices[0].message.content
        await asyncio.sleep(1.5)  # Add a small delay to respect rate limits
        
        # More robust parsing of the response
        summary = ""
        context = ""
        if "Summary:" in content and "Context:" in content:
            parts = content.split("Summary:", 1)
            if len(parts) > 1:
                summary_and_context = parts[1].split("Context:", 1)
                summary = summary_and_context[0].strip()
                if len(summary_and_context) > 1:
                    context = summary_and_context[1].strip()
        
        # If parsing fails, use the entire content as both summary and context
        if not summary and not context:
            summary = context = content.strip()
        
        return summary, context

    async def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            query_embedding = await self.llm_manager.get_embedding(query)
            await asyncio.sleep(1.5)  # Add a small delay to respect rate limits

            if not isinstance(query_embedding, list):
                logger.error(f"Invalid query embedding type: {type(query_embedding)}")
                raise ValueError(f"Invalid query embedding type: {type(query_embedding)}")

            if len(query_embedding) == 0:
                logger.error("Query embedding is empty")
                raise ValueError("Query embedding is empty")

            query_vector = np.array(query_embedding, dtype=np.float32)

            if self.vector_store.table is None:
                logger.warning("Vector store table does not exist yet. Returning empty results.")
                return []

            if self.vector_store.embedding_size is None:
                logger.error("Embedding size is not set")
                raise ValueError("Embedding size is not set")

            if len(query_vector) != self.vector_store.embedding_size:
                logger.error(f"Query embedding size ({len(query_vector)}) does not match expected size ({self.vector_store.embedding_size})")
                raise ValueError("Query embedding size mismatch")

            # Search using doc_embedding
            doc_results = self.vector_store.table.search(query_vector.tolist(), vector_column_name="doc_embedding") \
                .limit(top_k) \
                .select(["id", "concept", "summary", "context", "doc_embedding"]) \
                .metric("cosine") \
                .to_list()

            # Search using context_embedding
            context_results = self.vector_store.table.search(query_vector.tolist(), vector_column_name="context_embedding") \
                .limit(top_k) \
                .select(["id", "concept", "summary", "context", "context_embedding"]) \
                .metric("cosine") \
                .to_list()

            # Combine and sort results
            all_results = doc_results + context_results
            all_results.sort(key=lambda x: x["_distance"])

            # Remove duplicates, keeping the best score for each id
            seen_ids = set()
            unique_results = []
            for r in all_results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    unique_results.append(r)
                    if len(unique_results) == top_k:
                        break

            return [{
                "id": r["id"],
                "concept": r["concept"],
                "summary": r["summary"],
                "context": r["context"],
                "score": r["_distance"]
            } for r in unique_results]

        except Exception as e:
            logger.error(f"Error in RAGEngine search: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Embedding: {query_embedding if 'query_embedding' in locals() else 'Not generated'}")
            logger.error(traceback.format_exc())
            raise

    async def update(self, id: str, summary: str, context: str):
        try:
            # Generate embeddings for both summary and context
            doc_embedding = await self.llm_manager.get_embedding(summary)
            context_embedding = await self.llm_manager.get_embedding(context)

            # Update the vector store with new data and embeddings
            self.vector_store.update(id, summary, context, doc_embedding, context_embedding)
        except Exception as e:
            logger.error(f"Error updating RAGEngine: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def delete(self, id: str):
        self.vector_store.delete(id)

class VectorStore:
    def __init__(self, table_name: str):
        db_path = "vectors.lance"
        try:
            self.db = lancedb.connect(db_path)
        except Exception as e:
            logger.error(f"Failed to connect to the database: {str(e)}")
            raise
        self.llm_manager = LiteLLMManager()
        
        self.embedding_size = None
        
        self.table_name = table_name
        self.table = self._get_or_create_table()

    def _get_or_create_table(self):
        if self.table_name in self.db.table_names():
            table = self.db.open_table(self.table_name)
            self.embedding_size = table.schema.field("doc_embedding").type.list_size
            return table
        else:
            # We'll create the table with a placeholder schema
            # The actual schema will be set when we add the first item
            return None

    def add(self, concept: str, summary: str, context: str, doc_embedding: List[float], context_embedding: List[float]):
        unique_id = str(uuid.uuid4())
        
        doc_embedding_array = np.array(doc_embedding, dtype=np.float32)
        context_embedding_array = np.array(context_embedding, dtype=np.float32)
        
        if self.embedding_size is None:
            self.embedding_size = len(doc_embedding_array)
            
            if self.table is None:
                schema = pa.schema([
                    ("id", pa.string()),
                    ("concept", pa.string()),
                    ("summary", pa.string()),
                    ("context", pa.string()),
                    ("doc_embedding", pa.list_(pa.float32(), self.embedding_size)),
                    ("context_embedding", pa.list_(pa.float32(), self.embedding_size))
                ])
                self.table = self.db.create_table(self.table_name, schema=schema)

        if len(doc_embedding_array) != self.embedding_size or len(context_embedding_array) != self.embedding_size:
            raise ValueError(f"Expected embedding size {self.embedding_size}, but got {len(doc_embedding_array)} and {len(context_embedding_array)}")

        self.table.add([{
            "id": unique_id,
            "concept": concept,
            "summary": summary,
            "context": context,
            "doc_embedding": doc_embedding_array.tolist(),
            "context_embedding": context_embedding_array.tolist()
        }])

    
    

    def read(self, id: str):
        return self.table.to_pandas(filter=f"id = '{id}'").to_dict('records')[0]

    def update(self, id: str, summary: str, context: str, doc_embedding: List[float], context_embedding: List[float]):
        doc_embedding_array = np.array(doc_embedding, dtype=np.float32)
        context_embedding_array = np.array(context_embedding, dtype=np.float32)

        if len(doc_embedding_array) != self.embedding_size or len(context_embedding_array) != self.embedding_size:
            raise ValueError(f"Expected embedding size {self.embedding_size}, but got {len(doc_embedding_array)} and {len(context_embedding_array)}")

        self.table.update().where(f"id = '{id}'").set(
            summary=summary,
            context=context,
            doc_embedding=doc_embedding_array.tolist(),
            context_embedding=context_embedding_array.tolist()
        ).execute()

    def delete(self, id: str):
        self.table.delete().where(f"id = '{id}'").execute()
