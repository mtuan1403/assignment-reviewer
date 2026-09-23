import pytest
from pathlib import Path
from backend.app.models.domain import DocumentType
from backend.app.services.parser.factory import DocumentParserFactory
from backend.app.services.parser.pdf_parser import PDFDocumentParser
from backend.app.services.parser.docx_parser import DOCXDocumentParser
from backend.app.services.parser.base import EmptyDocumentException, ParsingException

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"


def test_parse_pdf():
    pdf_path = SAMPLE_DIR / "sample_student_draft.pdf"
    assert pdf_path.exists(), "Sample PDF must exist"

    parser = DocumentParserFactory.get_parser(pdf_path)
    assert isinstance(parser, PDFDocumentParser)

    meta, chunks = parser.parse(pdf_path, DocumentType.STUDENT_DRAFT)
    assert meta.page_count >= 1
    assert meta.char_count > 100
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.document_type == DocumentType.STUDENT_DRAFT
        assert chunk.page >= 1
        assert chunk.text.strip() != ""


def test_parse_docx():
    docx_path = SAMPLE_DIR / "sample_student_draft.docx"
    assert docx_path.exists(), "Sample DOCX must exist"

    parser = DocumentParserFactory.get_parser(docx_path)
    assert isinstance(parser, DOCXDocumentParser)

    meta, chunks = parser.parse(docx_path, DocumentType.STUDENT_DRAFT)
    assert meta.page_count >= 1
    assert meta.char_count > 100
    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.document_type == DocumentType.STUDENT_DRAFT
        assert chunk.page >= 1
        assert chunk.section != ""


def test_parse_empty_file(tmp_path):
    empty_txt = tmp_path / "empty.txt"
    empty_txt.write_text("")
    parser = DocumentParserFactory.get_parser(empty_txt)

    with pytest.raises(EmptyDocumentException):
        parser.parse(empty_txt, DocumentType.ASSIGNMENT_SPEC)


def test_invalid_extension(tmp_path):
    invalid_file = tmp_path / "test.xyz"
    invalid_file.write_text("hello")
    with pytest.raises(ParsingException):
        DocumentParserFactory.get_parser(invalid_file)
