from pathlib import Path
from typing import List, Tuple
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk, DocumentMetadata
from backend.app.services.parser.base import (
    BaseDocumentParser,
    ParsingException,
    EmptyDocumentException,
)
from backend.app.services.parser.pdf_parser import PDFDocumentParser
from backend.app.services.parser.docx_parser import DOCXDocumentParser


class TextDocumentParser(BaseDocumentParser):
    """Fallback parser for plain text / markdown files (useful in unit testing)."""

    def parse(self, file_path: Path, document_type: DocumentType) -> Tuple[DocumentMetadata, List[DocumentChunk]]:
        if not file_path.exists():
            raise ParsingException(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8", errors="ignore").strip()
        if not content:
            raise EmptyDocumentException("Text document is empty.")

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        chunks: List[DocumentChunk] = []
        current_section = "General"
        current_page = 1
        words_on_page = 0

        for i, para in enumerate(paragraphs):
            if para.startswith("#") or (len(para) < 60 and para.endswith(":")):
                current_section = para.lstrip("#").strip()

            words = len(para.split())
            words_on_page += words
            if words_on_page > 400:
                current_page += 1
                words_on_page = words

            chunk_id = f"{document_type.value}_p{current_page}_{i+1:04d}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_type=document_type,
                    page=current_page,
                    section=current_section,
                    text=para,
                    token_count=words,
                )
            )

        metadata = DocumentMetadata(
            filename=file_path.name,
            document_type=document_type,
            page_count=current_page,
            paragraph_count=len(paragraphs),
            char_count=len(content),
        )
        return metadata, chunks


class DocumentParserFactory:
    @staticmethod
    def get_parser(file_path: Path) -> BaseDocumentParser:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return PDFDocumentParser()
        elif suffix in [".docx", ".doc"]:
            return DOCXDocumentParser()
        elif suffix in [".txt", ".md"]:
            return TextDocumentParser()
        else:
            raise ParsingException(f"Unsupported file format '{suffix}'. Supported formats: PDF, DOCX, TXT.")
