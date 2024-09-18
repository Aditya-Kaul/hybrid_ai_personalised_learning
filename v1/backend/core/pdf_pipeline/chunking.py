"""
spacy model name:en_core_web_trf

"""
import os
import pymupdf4llm
import pathlib
from langchain.text_splitter import MarkdownTextSplitter
import spacy
from typing import List, Tuple
import matplotlib.pyplot as plt
from collections import Counter


def paragraphs(doc):
    start = 0
    for token in doc:
        if token.is_space and token.text.count("\n") > 1:
            yield doc[start:token.i]
            start = token.i
    yield doc[start:]


def chunk_pdf(file_path: str, out_path: str, chunk_size: int = 125, chunk_overlap: int = 10) -> List[str]:
    """
    Chunks a PDF file into smaller segments with configurable chunk size and overlap
    """
    md_text = pymupdf4llm.to_markdown(file_path)
    pathlib.Path(f"{out_path}/output.md").write_bytes(md_text.encode())

    nlp = spacy.load("en_core_web_trf")
    doc = nlp(md_text)
    paragraphs_list = list(paragraphs(doc))

    # Convert spaCy spans to strings
    paragraphs_text = [para.text for para in paragraphs_list]

    # Use MarkdownTextSplitter for  chunking
    splitter = MarkdownTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.create_documents(paragraphs_text)

    # Return the chunks as a list of strings
    return [chunk.page_content for chunk in chunks]


def prototype_chunks(file_path: str, out_path: str, sizes: List[int], overlaps: List[int]) -> List[Tuple[int, int, List[str]]]:
    """
    Prototype different chunk sizes and overlaps
    """
    results = []
    for size in sizes:
        for overlap in overlaps:
            chunks = chunk_pdf(file_path, out_path, size, overlap)
            results.append((size, overlap, chunks))
    return results


def visualize_chunks(results: List[Tuple[int, int, List[str]]]):
    """
    Visualize the chunking results
    """
    for size, overlap, chunks in results:
        print(f"\nChunk size: {size}, Overlap: {overlap}")
        print(f"Number of chunks: {len(chunks)}")
        if chunks:  # Check if chunks list is not empty
            print("First chunk:")
            # Print first 100 characters of first chunk
            print(chunks[0][:100] + "...")
            print("Last chunk:")
            # Print last 100 characters of last chunk
            print(chunks[-1][-100:] + "...")
        else:
            print("No chunks were generated.")
        print("-" * 50)


def plot_chunk_distribution(results: List[Tuple[int, int, List[str]]]):
    """
    Plot the frequency distribution of chunk sizes for each configuration
    """
    for size, overlap, chunks in results:
        if not chunks:
            print(f"No chunks to plot for size {size} and overlap {overlap}")
            continue

        chunk_lengths = [len(chunk) for chunk in chunks]

        plt.figure(figsize=(10, 6))
        plt.hist(chunk_lengths, bins=20, edgecolor='black')
        plt.title(
            f'Chunk Size Distribution (Target Size: {size}, Overlap: {overlap})')
        plt.xlabel('Chunk Size (characters)')
        plt.ylabel('Frequency')

        
        avg_size = sum(chunk_lengths) / len(chunk_lengths)
        max_size = max(chunk_lengths)
        min_size = min(chunk_lengths)

        plt.axvline(avg_size, color='r', linestyle='dashed',
                    linewidth=2, label=f'Average: {avg_size:.2f}')
        plt.axvline(max_size, color='g', linestyle='dashed',
                    linewidth=2, label=f'Max: {max_size}')
        plt.axvline(min_size, color='b', linestyle='dashed',
                    linewidth=2, label=f'Min: {min_size}')

        plt.legend()
        plt.show()

        # Print  statistics
        print(f"\nStatistics for Chunk Size: {size}, Overlap: {overlap}")
        print(f"Average chunk size: {avg_size:.2f}")
        print(f"Max chunk size: {max_size}")
        print(f"Min chunk size: {min_size}")
        print(
            f"Standard deviation: {(sum((x - avg_size) ** 2 for x in chunk_lengths) / len(chunk_lengths)) ** 0.5:.2f}")

        # Display most common chunk sizes
        counter = Counter(chunk_lengths)
        print("\nMost common chunk sizes:")
        for length, count in counter.most_common(5):
            print(f"  {length}: {count} occurrences")
        print("-" * 50)


if __name__ == "__main__":
    file_path = "/home/tso/hybrid_ai_personalised_learning/v1/backend/core/pdf_pipeline/input.pdf"
    out_path = "v1/backend/core/pdf_pipeline"

    # Define ranges for chunk sizes and overlaps to test
    chunk_sizes = [20, 50, 100]
    chunk_overlaps = [5, 10, 20]

    results = prototype_chunks(
        file_path, out_path, chunk_sizes, chunk_overlaps)
    visualize_chunks(results)
    plot_chunk_distribution(results)
