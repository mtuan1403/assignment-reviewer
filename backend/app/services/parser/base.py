from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
from backend.app.models.domain import DocumentType
from backend.app.models.schemas import DocumentChunk, DocumentMetadata


class ParsingException(Exception):
    pass


class EmptyDocumentException(ParsingException):
    pass


class ScannedDocumentException(ParsingException):
    pass


class BaseDocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path, document_type: DocumentType) -> tuple[DocumentMetadata, List[DocumentChunk]]:
        """
        Extract text while preserving:
        - document name
        - page number
        - section heading where possible
        - paragraph/chunk ID
        Returns (metadata, raw_chunks)
        """
        pass
