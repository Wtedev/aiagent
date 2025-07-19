from langchain.text_splitter import RecursiveCharacterTextSplitter

def create_splitter(chunk_size: int = 1000, chunk_overlap: int = 200):
    """Create and return a consistent text splitter."""
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
