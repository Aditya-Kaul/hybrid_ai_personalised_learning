import pytest
import asyncio
from unittest.mock import Mock, patch
from backend.app.services.rag_engine import RAGEngine, VectorStore
from backend.app.services.litellm_base import LiteLLMManager


@pytest.fixture
def mock_llm_manager():
    with patch('rag_engine.LiteLLMManager') as mock:
        yield mock

@pytest.fixture
def mock_vector_store():
    with patch('rag_engine.VectorStore') as mock:
        yield mock

@pytest.fixture
def rag_engine(mock_llm_manager, mock_vector_store):
    return RAGEngine()

@pytest.mark.asyncio
async def test_process_chunks(rag_engine, mock_llm_manager):
    chunks = ["chunk1", "chunk2", "chunk3"]
    mock_llm_manager.return_value.completion_with_retries.return_value.choices = [
        Mock(message=Mock(content="concept1, concept2"))
    ]
    mock_llm_manager.return_value.get_embedding.return_value = [0.1] * 1024

    await rag_engine.process_chunks(chunks)

    assert mock_llm_manager.return_value.completion_with_retries.call_count == 3
    assert mock_llm_manager.return_value.get_embedding.call_count == 2
    assert rag_engine.vector_store.create.call_count == 2

@pytest.mark.asyncio
async def test_search(rag_engine, mock_llm_manager):
    query = "test query"
    mock_llm_manager.return_value.get_embedding.return_value = [0.1] * 1024
    rag_engine.vector_store.search.return_value = [
        {"id": "1", "concept": "concept1", "summary": "summary1", "context": "context1", "score": 0.9}
    ]

    result = await rag_engine.search(query)

    mock_llm_manager.return_value.get_embedding.assert_called_once_with(query)
    rag_engine.vector_store.search.assert_called_once_with([0.1] * 1024, 5)
    assert len(result) == 1
    assert result[0]["id"] == "1"

def test_vector_store_create(mock_vector_store):
    vector_store = VectorStore("test_table")
    vector_store.create("concept1", "summary1", "context1", [0.1] * 1024)

    vector_store.table.add.assert_called_once_with([{
        "id": "concept1",
        "concept": "concept1",
        "summary": "summary1",
        "context": "context1",
        "embedding": [0.1] * 1024
    }])

def test_vector_store_search(mock_vector_store):
    vector_store = VectorStore("test_table")
    mock_vector_store.return_value.table.search.return_value.limit.return_value.to_list.return_value = [
        {"id": "1", "concept": "concept1", "summary": "summary1", "context": "context1", "_distance": 0.9}
    ]

    result = vector_store.search([0.1] * 1024)

    vector_store.table.search.assert_called_once_with([0.1] * 1024)
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["score"] == 0.9

def test_vector_store_update(mock_vector_store):
    vector_store = VectorStore("test_table")
    vector_store.update("1", "new_summary", "new_context", [0.2] * 1024)

    vector_store.table.update.return_value.where.return_value.set.assert_called_once_with(
        summary="new_summary",
        context="new_context",
        embedding=[0.2] * 1024
    )

def test_vector_store_delete(mock_vector_store):
    vector_store = VectorStore("test_table")
    vector_store.delete("1")

    vector_store.table.delete.return_value.where.assert_called_once_with("id = '1'")
    vector_store.table.delete.return_value.where.return_value.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main()