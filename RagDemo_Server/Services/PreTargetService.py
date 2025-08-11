from fastapi import UploadFile, File
from transformers import AutoTokenizer, AutoModel
from docx import Document
import pdfplumber
import io


class PreTargetService:
    def __init__(
        self,
        model: str = "intfloat/multilingual-e5-large",
        storeDataPath: str = "./VectorStore/",
    ):
        self._tokenizer = AutoTokenizer.from_pretrained(model)
        self._model = AutoModel.from_pretrained(model)
        self._storeDataPath = storeDataPath

    async def SplitText(
        self, file: UploadFile = File(), maxToken: int = 100
    ) -> list[str]:
        contents = await file.read()
        if not file.filename:
            raise ValueError("Error of file name")

        texts = ""
        if file.filename.endswith("docx"):
            texts = self.ReadDocxContent(io.BytesIO(contents))
        elif file.filename.endswith("pdf"):
            texts = self.ReadPdfContent(io.BytesIO(contents))
        else:
            raise ValueError("Error type of the file")
        tokens = self._tokenizer.encode(texts)

        chunks = []

        for i in range(0, len(tokens), maxToken):
            chunkTokens = tokens[i : i + maxToken]
            chunkTexts = self._tokenizer.decode(chunkTokens)
            chunks.append(chunkTexts)

        return chunks

    @staticmethod
    def ReadDocxContent(IOByteFile: io.BytesIO) -> str | None:
        try:
            document = Document(IOByteFile)
            fullText = []
            for paragraph in document.paragraphs:
                fullText.append(paragraph.text)
            return "".join(fullText)
        except Exception as ex:
            print(f"Error reading DOCX file: {ex}")
            return None

    @staticmethod
    def ReadPdfContent(IOByteFile: io.BytesIO) -> str | None:
        try:
            fullText = []
            pdfDoc = pdfplumber.open(IOByteFile)
            for page in pdfDoc.pages:
                fullText.append(page.extract_text())
            pdfDoc.close()
            return "".join(fullText)
        except Exception as ex:
            print(f"Error reading PDF file: {ex}")
            return None
