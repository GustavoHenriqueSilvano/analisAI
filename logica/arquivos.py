from fastapi import UploadFile
import io
from typing import Optional
from PyPDF2 import PdfReader

class FileHandler:
    @staticmethod
    async def read_file(file: UploadFile) -> str:
        """
        Lê o conteúdo de arquivos PDF ou TXT.
        Retorna texto extraído.
        """
        if not file.filename.lower().endswith(('.pdf', '.txt')):
            raise ValueError(f"Formato não suportado: {file.filename}")

        content = ""
        if file.filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(await file.read()))
            for page in reader.pages:
                content += page.extract_text() + "\n"
        elif file.filename.lower().endswith(".txt"):
            content = (await file.read()).decode('utf-8')

        return content.strip()
