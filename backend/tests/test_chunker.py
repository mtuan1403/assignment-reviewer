from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk
from backend.app.services.chunker.assignment_chunker import AssignmentChunker


def test_section_aware_chunking():
    chunker = AssignmentChunker(target_words=50, max_words=80)
    raw_chunks = [
        DocumentChunk(
            chunk_id="raw_1",
            document_type=DocumentType.STUDENT_DRAFT,
            page=1,
            section="1. Introduction",
            text="This is the introduction paragraph describing the background of the system.",
            token_count=10,
        ),
        DocumentChunk(
            chunk_id="raw_2",
            document_type=DocumentType.STUDENT_DRAFT,
            page=1,
            section="1. Introduction",
            text="Another sentence elaborating on the core architectural scope.",
            token_count=9,
        ),
        DocumentChunk(
            chunk_id="raw_3",
            document_type=DocumentType.STUDENT_DRAFT,
            page=2,
            section="2. Analysis",
            text="Moving into the detailed analytical trade-offs of microservices.",
            token_count=8,
        ),
    ]

    semantic_chunks = chunker.chunk_document(raw_chunks, DocumentType.STUDENT_DRAFT)

    # Section boundary should have created separate chunks for Introduction and Analysis
    sections = [c.section for c in semantic_chunks]
    assert "1. Introduction" in sections
    assert "2. Analysis" in sections
    for sc in semantic_chunks:
        assert sc.chunk_id.startswith("chunk_")
        assert sc.page in [1, 2]
        assert sc.text != ""


def test_long_paragraph_splitting():
    chunker = AssignmentChunker(target_words=30, max_words=40, overlap_sentences=1)
    sentences = [f"Sentence number {i} provides detailed discussion." for i in range(15)]
    long_text = " ".join(sentences)

    raw_chunks = [
        DocumentChunk(
            chunk_id="raw_long",
            document_type=DocumentType.STUDENT_DRAFT,
            page=3,
            section="Deep Dive",
            text=long_text,
            token_count=len(long_text.split()),
        )
    ]

    sub_chunks = chunker.chunk_document(raw_chunks)
    assert len(sub_chunks) > 1
    for sc in sub_chunks:
        assert sc.page == 3
        assert sc.section == "Deep Dive"
        assert sc.token_count <= 45
