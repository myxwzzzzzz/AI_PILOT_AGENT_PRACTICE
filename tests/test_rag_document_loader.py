import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from rag_document_loader import (
    list_document_files,
    build_document_chunks,
)


print("测试 1：列出 documents 目录下的文档")
files = list_document_files()
for file in files:
    print("-", file)


print("\n测试 2：构建文档 chunks")
chunks = build_document_chunks(
    chunk_size=300,
    overlap=50,
)

print("chunk 数量：", len(chunks))

for chunk in chunks[:5]:
    print("=" * 80)
    print("chunk_id:", chunk["chunk_id"])
    print("source:", chunk["source"])
    print("chunk_index:", chunk["chunk_index"])
    print("text:")
    print(chunk["text"])