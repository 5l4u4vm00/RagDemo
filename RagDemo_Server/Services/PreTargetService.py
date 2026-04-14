import io
from fastapi import UploadFile, File
from transformers import AutoTokenizer, AutoModel
from docx import Document
import pdfplumber
from torch import Tensor
import torch.nn.functional as F
from sklearn.metrics.pairwise import cosine_similarity

from Database.db import get_conn


class PreTargetService:
    def __init__(
        self,
        model: str = "intfloat/multilingual-e5-large",
    ):
        self._tokenizer = AutoTokenizer.from_pretrained(model)
        self._model = AutoModel.from_pretrained(model)

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
        elif file.filename.endswith("cs"):
            texts = self.ReadCSFile(io.BytesIO(contents))
        else:
            raise ValueError("Error type of the file")
        tokens = self._tokenizer.encode(texts)

        chunks = []

        for i in range(0, len(tokens), maxToken):
            chunkTokens = tokens[i : i + maxToken]
            chunkTexts = self._tokenizer.decode(chunkTokens)
            chunks.append(chunkTexts)

        return chunks

    def EmbeddingTexts(self, texts: list[str], dataName: str):
        allEmbeddings: list[list[float]] = []
        batch: int = 10
        for i in range(0, len(texts), batch):
            inputs = self._tokenizer(
                texts[i : i + batch],
                padding=True,
                max_length=512,
                truncation=True,
                return_tensors="pt",
            )
            outputs = self._model(**inputs)
            embeddings = self.AveragePool(
                outputs.last_hidden_state, inputs["attention_mask"]
            )
            allEmbeddings.extend(F.normalize(embeddings, p=2, dim=1).tolist())

        self._StoreToDatabase(texts, allEmbeddings, dataName)

    def _StoreToDatabase(
        self,
        texts: list[str],
        embeddings: list[list[float]],
        dataName: str,
    ):
        threshold = 0.8
        similarities = cosine_similarity(embeddings)

        with get_conn() as conn:
            with conn.cursor() as cur:
                # Upsert dataset row, get its id
                cur.execute(
                    """
                    INSERT INTO datasets (name)
                    VALUES (%s)
                    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                    RETURNING id;
                    """,
                    (dataName,),
                )
                dataset_id = cur.fetchone()[0]

                # Remove existing data for clean re-embed
                cur.execute(
                    "DELETE FROM chunk_edges WHERE dataset_id = %s;", (dataset_id,)
                )
                cur.execute(
                    "DELETE FROM chunks WHERE dataset_id = %s;", (dataset_id,)
                )

                # Insert chunks with embeddings
                for idx, (text, emb) in enumerate(zip(texts, embeddings)):
                    cur.execute(
                        """
                        INSERT INTO chunks (dataset_id, chunk_idx, text, embedding)
                        VALUES (%s, %s, %s, %s::vector);
                        """,
                        (dataset_id, idx, text, str(emb)),
                    )

                # Insert edges for chunk pairs with cosine similarity >= threshold
                for i in range(len(texts)):
                    for j in range(i + 1, len(texts)):
                        sim = float(similarities[i][j])
                        if sim >= threshold:
                            cur.execute(
                                """
                                INSERT INTO chunk_edges
                                    (dataset_id, src_idx, dst_idx, weight)
                                VALUES (%s, %s, %s, %s);
                                """,
                                (dataset_id, i, j, sim),
                            )

    @staticmethod
    def AveragePool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

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

    @staticmethod
    def ReadCSFile(IOByteFile: io.BytesIO) -> str | None:
        try:
            content = IOByteFile.read().decode("utf-8")
            return content
        except Exception as ex:
            print(f"Error reading CS file: {ex}")
            return None
