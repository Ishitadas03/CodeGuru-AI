import io
import logging
from typing import Dict, List, Any
from pypdf import PdfReader

logger = logging.getLogger("codeguru.rag.pdf")


class PDFService:
    """Service to parse PDF files and split their content into semantic chunks."""

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract text page-by-page from PDF bytes.

        Returns:
            A list of dicts: [{"page": page_num, "text": page_text}]
        """
        pages = []
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append({
                    "page": i + 1,
                    "text": text.strip()
                })
        except Exception as e:
            logger.error(f"Failed to parse PDF bytes: {e}", exc_info=True)
            raise ValueError(f"Invalid PDF file format: {e}")
        return pages

    def chunk_pages(
        self,
        pages: List[Dict[str, Any]],
        chunk_size: int = 750,
        chunk_overlap: int = 150
    ) -> List[Dict[str, Any]]:
        """Chunk page-level text into overlapping segments while preserving word boundaries.

        Returns:
            A list of chunks: [{"text": chunk_text, "page": page_num, "chunk_index": idx}]
        """
        chunks = []
        chunk_index = 0

        for page in pages:
            page_num = page["page"]
            text = page["text"]
            if not text:
                continue

            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]
                
                # Adjust to the last space to avoid cutting off words in middle
                if end < len(text):
                    last_space = chunk_text.rfind(" ")
                    if last_space > chunk_size // 2:
                        end = start + last_space
                        chunk_text = text[start:end]

                chunks.append({
                    "text": chunk_text.strip(),
                    "page": page_num,
                    "chunk_index": chunk_index
                })
                chunk_index += 1
                
                # Advance by the length of the chunk minus overlap
                start += max(1, len(chunk_text) - chunk_overlap)

        return chunks
