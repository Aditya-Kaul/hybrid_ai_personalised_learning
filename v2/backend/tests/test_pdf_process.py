
from unittest.mock import patch, MagicMock
import pytest
from backend.app.services.pdf_process import PDFProcessor 

@pytest.fixture
def pdf_processor():
    return PDFProcessor()

def test_init():
    processor = PDFProcessor(chunk_size=200, chunk_overlap=20)
    assert processor.chunk_size == 200
    assert processor.chunk_overlap == 20
    assert processor.nlp is not None

def test_paragraphs(pdf_processor):
    mock_doc = MagicMock()
    mock_doc.__iter__.return_value = [
        MagicMock(is_space=True, text="\n\n", i=2),
        MagicMock(is_space=False, text="text", i=3),
        MagicMock(is_space=True, text="\n\n\n", i=5)
    ]
    mock_doc.__getitem__.side_effect = lambda s: MagicMock(text=f"para{s}")

    paragraphs = list(pdf_processor.paragraphs(mock_doc))
    assert len(paragraphs) == 3
    assert [p.text for p in paragraphs] == ["para0:2", "para2:5", "para5:"]

@patch('your_module.pymupdf4llm.to_markdown')
@patch('your_module.MarkdownTextSplitter')
def test_chunk_pdf(mock_splitter, mock_to_markdown, pdf_processor):
    mock_to_markdown.return_value = "Test markdown content"
    mock_splitter_instance = MagicMock()
    mock_splitter.return_value = mock_splitter_instance
    mock_splitter_instance.create_documents.return_value = [
        MagicMock(page_content="Chunk 1"),
        MagicMock(page_content="Chunk 2")
    ]

    result = pdf_processor.chunk_pdf(b"fake pdf data")

    mock_to_markdown.assert_called_once_with(b"fake pdf data")
    mock_splitter.assert_called_once_with(chunk_size=125, chunk_overlap=10)
    mock_splitter_instance.create_documents.assert_called_once()
    assert result == ["Chunk 1", "Chunk 2"]

def test_process_pdf(pdf_processor):
    with patch.object(pdf_processor, 'chunk_pdf') as mock_chunk_pdf:
        mock_chunk_pdf.return_value = ["Chunk 1", "Chunk 2"]
        result = pdf_processor.process_pdf(b"fake pdf data")
        mock_chunk_pdf.assert_called_once_with(b"fake pdf data")
        assert result == ["Chunk 1", "Chunk 2"]

# Add more tests as needed for edge cases and error handling

print("Successfully imported modules from backend.app.services")