from pathlib import Path
from typing import List, Tuple
import re
import fitz  # PyMuPDF

from backend.app.core.logging import get_logger
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk, DocumentMetadata
from backend.app.services.parser.base import (
    BaseDocumentParser,
    EmptyDocumentException,
    ScannedDocumentException,
    ParsingException,
)

logger = get_logger(__name__)


class PDFDocumentParser(BaseDocumentParser):
    def parse(self, file_path: Path, document_type: DocumentType) -> Tuple[DocumentMetadata, List[DocumentChunk]]:
        if not file_path.exists():
            raise ParsingException(f"File not found: {file_path}")

        try:
            doc = fitz.open(str(file_path))
        except Exception as e:
            raise ParsingException(f"Corrupted or invalid PDF file: {e}")

        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise EmptyDocumentException("PDF document contains no pages.")

        chunks: List[DocumentChunk] = []
        total_chars = 0
        total_paragraphs = 0
        current_section = "Introduction / Overview"

        chunk_counter = 1

        heading_pattern = re.compile(
            r"^(?:(?:\d+\.)+\d*|\b(?:Section|Chapter|Part|Module)\s+\d+)\s+[\w\s]{3,60}$",
            re.IGNORECASE,
        )

        for page_num in range(1, total_pages + 1):
            page = doc[page_num - 1]
            text_dict = page.get_text("dict")
            blocks = text_dict.get("blocks", [])

            for block in blocks:
                # We only care about text blocks (type 0)
                if block.get("type") != 0:
                    continue

                block_lines: List[str] = []
                is_heading_block = False

                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    line_text = "".join(span.get("text", "") for span in spans).strip()
                    if not line_text:
                        continue

                    # Check if font size or formatting suggests a heading
                    max_size = max((span.get("size", 10.0) for span in spans), default=10.0)
                    is_bold = any("bold" in span.get("font", "").lower() for span in spans)

                    if (max_size >= 13.0 or is_bold) and len(line_text) < 80:
                        is_heading_block = True
                        current_section = line_text

                    block_lines.append(line_text)

                combined_text = " ".join(block_lines).strip()
                if not combined_text:
                    continue

                # Also regex match section headings
                if heading_pattern.match(combined_text):
                    current_section = combined_text

                total_chars += len(combined_text)
                total_paragraphs += 1

                chunk_id = f"{document_type.value}_p{page_num}_{chunk_counter:04d}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_type=document_type,
                        page=page_num,
                        section=current_section,
                        text=combined_text,
                        token_count=len(combined_text.split()),
                    )
                )
                chunk_counter += 1

        doc.close()

        if total_chars == 0:
            raise ScannedDocumentException(
                "The PDF contains 0 extractable text characters. It is likely a scanned image. "
                "Please provide a text-searchable PDF."
            )

        metadata = DocumentMetadata(
            filename=file_path.name,
            document_type=document_type,
            page_count=total_pages,
            paragraph_count=total_paragraphs,
            char_count=total_chars,
        )

        logger.info(
            f"Successfully parsed PDF '{file_path.name}': {total_pages} pages, "
            f"{len(chunks)} raw chunks, {total_chars} chars."
        )
        return metadata, chunks
