from pathlib import Path
from typing import Set
import logging
from core.interfaces.parser import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """
    Specialized PDF parser that supports multiple strategies:
    - 'markitdown': Uses Microsoft's MarkItDown (lightweight, default)
    - 'docling': Uses IBM's Docling (higher accuracy, heavier)
    """

    def __init__(self, strategy: str = "markitdown"):
        self.strategy = strategy.lower()
        if self.strategy not in ("markitdown", "docling"):
            raise ValueError(f"Unknown PDF parser strategy: {strategy}. Use 'markitdown' or 'docling'.")
        self._parser_instance = None  # Lazy initialization

    def _ensure_initialized(self):
        """Lazy initialize the underlying parser on first use."""
        if self._parser_instance is not None:
            return

        if self.strategy == "markitdown":
            try:
                from markitdown import MarkItDown
                self._parser_instance = MarkItDown()
            except ImportError as e:
                raise ImportError(
                    f"MarkItDown not installed: {e}. Please run: pip install markitdown"
                )
        elif self.strategy == "docling":
            try:
                from docling.document_converter import DocumentConverter
                self._parser_instance = DocumentConverter()
            except ImportError as e:
                raise ImportError(
                    f"Docling not installed: {e}. Please run: pip install docling"
                )

    def get_supported_extensions(self) -> Set[str]:
        return {'.pdf'}

    def parse(self, file_path: Path, **kwargs) -> str:
        """Parse a PDF file using the configured strategy."""
        use_ocr = kwargs.get('use_ocr', True)

        self._ensure_initialized()

        try:
            if self.strategy == "markitdown":
                return self._parse_with_markitdown(file_path, use_ocr)
            elif self.strategy == "docling":
                return self._parse_with_docling(file_path)
        except Exception as e:
            logger.error(f"PDF parsing failed ({self.strategy}) for {file_path}: {e}")
            raise

    def _parse_with_markitdown(self, file_path: Path, use_ocr: bool = True) -> str:
        """Parse PDF using MarkItDown."""
        result = self._parser_instance.convert(str(file_path), use_ocr=use_ocr)
        return result.text_content or ""

    def _parse_with_docling(self, file_path: Path) -> str:
        """Parse PDF using Docling for higher accuracy."""
        result = self._parser_instance.convert(str(file_path))
        document = result.document
        return document.export_to_markdown() if document else ""
