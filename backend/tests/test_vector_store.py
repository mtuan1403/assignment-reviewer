import pytest
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk
from backend.app.services.vector_store.chroma_service import ChromaVectorStore


def test_chroma_vector_store(tmp_path):
    store = ChromaVectorStore(persist_directory=tmp_path)
    review_id = "test_review_session_01"

    chunks = [
        DocumentChunk(
            chunk_id="chunk_01",
            document_type=DocumentType.STUDENT_DRAFT,
            page=1,
            section="Architecture",
            text="Kubernetes orchestrates containerized services with horizontal pod autoscaling.",
            token_count=8,
        ),
        DocumentChunk(
            chunk_id="chunk_02",
            document_type=DocumentType.STUDENT_DRAFT,
            page=2,
            section="Governance",
            text="Ethical AI governance requires demographic fairness audits and GDPR data protection.",
            token_count=10,
        ),
    ]

    indexed_count = store.index_chunks(review_id, chunks)
    assert indexed_count == 2

    # Query for Kubernetes
    results = store.query_similar(review_id, "container orchestration Kubernetes autoscaling", top_k=1)
    assert len(results) == 1
    assert "Kubernetes" in results[0].text
    assert results[0].page == 1

    # Query for Ethics
    results_eth = store.query_similar(review_id, "GDPR privacy compliance ethical algorithms", top_k=1)
    assert len(results_eth) == 1
    assert "Ethical" in results_eth[0].text

    # All chunks
    all_chunks = store.get_all_chunks(review_id)
    assert len(all_chunks) == 2

    # Clean up
    store.delete_collection(review_id)
