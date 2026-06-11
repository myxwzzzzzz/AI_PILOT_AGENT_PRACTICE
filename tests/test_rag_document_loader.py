from rag_document_loader import build_document_chunks, list_document_files


def test_list_document_files():
    files = list_document_files()

    assert isinstance(files, list)
    assert len(files) > 0
    assert all(file.suffix in {".md", ".txt"} for file in files)


def test_build_document_chunks():
    chunks = build_document_chunks(chunk_size=300, overlap=50)

    assert isinstance(chunks, list)
    assert len(chunks) > 0

    first_chunk = chunks[0]
    assert "source" in first_chunk
    assert "chunk_id" in first_chunk
    assert "chunk_index" in first_chunk
    assert "text" in first_chunk
