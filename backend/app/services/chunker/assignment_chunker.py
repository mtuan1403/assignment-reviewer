from typing import List
import re
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk
from backend.app.core.logging import get_logger

logger = get_logger(__name__)


class AssignmentChunker:
    def __init__(self, target_words: int = 250, max_words: int = 350, overlap_sentences: int = 1):
        self.target_words = target_words
        self.max_words = max_words
        self.overlap_sentences = overlap_sentences

    def chunk_document(
        self, raw_chunks: List[DocumentChunk], document_type: DocumentType = DocumentType.STUDENT_DRAFT
    ) -> List[DocumentChunk]:
        """
        Performs section-aware and paragraph-aware chunking.
        Respects section boundaries, page provenance, and reasonable word/token limits.
        """
        if not raw_chunks:
            return []

        processed_chunks: List[DocumentChunk] = []
        chunk_idx = 1

        # Group by section and page
        current_section = None
        current_page = None
        buffer_text_list: List[str] = []
        buffer_words = 0

        sentence_splitter = re.compile(r"(?<=[.?!])\s+(?=[A-Z0-9])")

        def flush_buffer():
            nonlocal chunk_idx, buffer_text_list, buffer_words
            if not buffer_text_list:
                return
            combined_text = "\n\n".join(buffer_text_list).strip()
            if combined_text:
                processed_chunks.append(
                    DocumentChunk(
                        chunk_id=f"chunk_{chunk_idx:04d}",
                        document_type=document_type,
                        page=current_page or 1,
                        section=current_section or "General",
                        text=combined_text,
                        token_count=len(combined_text.split()),
                    )
                )
                chunk_idx += 1
            buffer_text_list = []
            buffer_words = 0

        for item in raw_chunks:
            # If section or page changed, flush current buffer
            if item.section != current_section or item.page != current_page:
                flush_buffer()
                current_section = item.section
                current_page = item.page

            item_words = len(item.text.split())

            # If this single paragraph is very large, split by sentences
            if item_words > self.max_words:
                flush_buffer()
                sentences = sentence_splitter.split(item.text)
                sub_buffer: List[str] = []
                sub_count = 0

                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    w_count = len(sent.split())
                    if sub_count + w_count > self.max_words and sub_buffer:
                        processed_chunks.append(
                            DocumentChunk(
                                chunk_id=f"chunk_{chunk_idx:04d}",
                                document_type=document_type,
                                page=current_page,
                                section=current_section,
                                text=" ".join(sub_buffer),
                                token_count=sub_count,
                            )
                        )
                        chunk_idx += 1
                        # Overlap
                        sub_buffer = sub_buffer[-self.overlap_sentences :] if self.overlap_sentences > 0 else []
                        sub_count = sum(len(s.split()) for s in sub_buffer)

                    sub_buffer.append(sent)
                    sub_count += w_count

                if sub_buffer:
                    processed_chunks.append(
                        DocumentChunk(
                            chunk_id=f"chunk_{chunk_idx:04d}",
                            document_type=document_type,
                            page=current_page,
                            section=current_section,
                            text=" ".join(sub_buffer),
                            token_count=sub_count,
                        )
                    )
                    chunk_idx += 1

            # Normal paragraph: check if adding it exceeds target
            elif buffer_words + item_words > self.max_words:
                flush_buffer()
                buffer_text_list.append(item.text)
                buffer_words += item_words
            else:
                buffer_text_list.append(item.text)
                buffer_words += item_words

        flush_buffer()

        logger.info(
            f"Chunked document into {len(processed_chunks)} semantic chunks "
            f"(target words ~{self.target_words}, max {self.max_words})."
        )
        return processed_chunks
