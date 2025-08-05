import os
import ollama
import tiktoken
import faiss
import json
import numpy as np
import pdfplumber
import networkx as nx
from dotenv import load_dotenv
from openai import AzureOpenAI
from ollama import ChatResponse
from openai.types.chat.completion_create_params import ChatCompletionMessageParam
from docx import Document
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
_openAIKey = os.environ.get("AZURE_OPENAI_KEY")
_openAIEndpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
_faissPath = "./VectorStore/vectorDB.faiss"
_jsonPath = "./VectorStore/textList.json"
_nxPath = "./VectorStore/graphDB.graphml"
_documentPath = "./documents/"

if not _openAIKey:
    raise ValueError("⚠️ 環境變數 AZURE_OPENAI_KEY 尚未設定")

if not _openAIEndpoint:
    raise ValueError("⚠️ 環境變數 AZURE_OPENAI_ENDPOINT 尚未設定")

_openAIClient = AzureOpenAI(
    azure_endpoint=_openAIEndpoint, api_key=_openAIKey, api_version="2024-05-01-preview"
)


class AIService:
    def __init__(self):
        self.messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": "你是一個智慧助理，請使用繁體中文回答。"}
        ]

    async def AskLlama(self, user_input: str, model: str = "gemma3n:e4b") -> str | None:
        """
        Ask question to local model
        """
        client = ollama.AsyncClient()

        prompts = self.SimilarQueryAndReturnPrompts(user_input, top_k=2, mode="graph")
        messages = self.messages.copy()
        messages.append({"role": "user", "content": prompts})
        response: ChatResponse = await client.chat(model=model, messages=messages)
        return response.message.content

    def AskOpenAI(self, user_input: str, model: str = "gpt-4.1") -> str | None:
        """
        Ask question to openai model
        """
        prompts = self.SimilarQueryAndReturnPrompts(user_input, top_k=2)
        messages = self.messages.copy()
        messages.append({"role": "user", "content": prompts})
        response = _openAIClient.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content

    @classmethod
    def SimilarQueryAndReturnPrompts(
        cls, question: str, top_k: int = 5, mode: str = "graph"
    ):
        match mode:
            case "graph":
                contextChunks = cls.SearchGraphRag(question, top_k)
            case _:
                contextChunks = cls.SearchSimilar(question, top_k)
        prompts = cls.BuildPrompt(question, contextChunks)
        return prompts

    @classmethod
    def EmbeddingFileInFolder(cls):
        """
        Read and embedding the file in documents, and store the rsult in the data base file.
        """
        chunkTexts = []
        for fileName in os.listdir(_documentPath):
            content = ""
            match fileName.split(".")[-1].lower():
                case "pdf":
                    content = cls.ReadPdfContent(_documentPath + fileName)
                case "docx":
                    content = cls.ReadDocxContent(_documentPath + fileName)
                case _:
                    continue
            if not content:
                continue
            chunkText = cls.SplitTextByTokens(text=content, maxTokens=100)
            chunkTexts.extend(chunkText)

        embeddings = cls.EmbeddingText(chunkTexts)
        cls.CreatGraphAndStore(chunkTexts, embeddings)
        if os.path.isfile(_faissPath):
            os.remove(_faissPath)
        cls.StoreVectorInfile(embeddings, _faissPath)
        jsonFile = open(_jsonPath, "w")
        json.dump(chunkTexts, jsonFile)
        jsonFile.close()
        return embeddings

    @staticmethod
    def CreatGraphAndStore(chunkTexts: list[str], embeddings: list[list[float]]):
        threshold = 0.65
        similarities = cosine_similarity(embeddings)
        G = nx.DiGraph()
        # Add node
        for i, chunk in enumerate(chunkTexts):
            G.add_node(i, text=chunk)

        # Add edage
        for i in range(len(chunkTexts)):
            for j in range(i + 1, len(chunkTexts)):
                sim = similarities[i][j]
                if sim >= threshold:
                    G.add_edge(i, j, weight=sim)
        nx.write_graphml(G, _nxPath)

    @staticmethod
    def ReadDocxContent(filepath: str) -> str | None:
        try:
            document = Document(filepath)
            fullText = []
            for paragraph in document.paragraphs:
                fullText.append(paragraph.text)
            return "".join(fullText)
        except Exception as ex:
            print(f"Error reading DOCX file: {ex}")
            return None

    @staticmethod
    def ReadPdfContent(filepath: str) -> str | None:
        try:
            fullText = []
            pdfDoc = pdfplumber.open(filepath)
            for page in pdfDoc.pages:
                fullText.append(page.extract_text())
            pdfDoc.close()
            return "".join(fullText)
        except Exception as ex:
            print(f"Error reading PDF file: {ex}")
            return None

    @staticmethod
    def SplitTextByTokens(
        text: str, maxTokens: int, model: str = "text-embedding-3-small"
    ) -> list[str]:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)

        chunks = []
        for i in range(0, len(tokens), maxTokens):
            chunkTokens = tokens[i : i + maxTokens]
            chunkText = encoding.decode(chunkTokens)
            chunks.append(chunkText)

        return chunks

    @staticmethod
    def EmbeddingText(
        texts: list[str], model: str = "text-embedding-3-small"
    ) -> list[list[float]]:
        response = _openAIClient.embeddings.create(input=texts, model=model)
        return [d.embedding for d in response.data]

    @staticmethod
    def StoreVectorInfile(embeddings: list[list[float]], filePath: str):
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)

        npEmbeddings = np.array(embeddings).astype("float32")
        index.add(npEmbeddings)

        faiss.write_index(index, filePath)

    @staticmethod
    def LoadVectorFile(filePath: str) -> faiss.Index:
        index = faiss.read_index(filePath)
        return index

    @classmethod
    def SearchSimilar(
        cls, question: str, top_k: int = 5, model="text-embedding-3-small"
    ):
        jsonFile = open(_jsonPath, "r")
        texts = json.load(jsonFile)
        index = cls.LoadVectorFile(_faissPath)

        questionVector = np.array(
            cls.EmbeddingText(texts=[question], model=model)
        ).astype("float32")

        distances, indices = index.search(questionVector, k=top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            result_text = texts[idx]
            results.append(result_text)

        if jsonFile:
            jsonFile.close()

        return results

    @staticmethod
    def BuildPrompt(question: str, context_chunks: list[str]) -> str:
        context_text = "\n\n".join(context_chunks)
        prompt = f"""根據以下資料回答問題：
        
        {context_text}
        
        問題：{question}
        請用中文簡潔、準確回答。
        若資料沒有相關內容則不提供相關答案
        """
        return prompt

    @classmethod
    def SearchGraphRag(cls, query: str, top_k=2):
        index = cls.LoadVectorFile(_faissPath)
        G = nx.read_graphml(_nxPath, node_type=int)

        queryVector = np.array(cls.EmbeddingText([query])).astype("float32")
        distances, indices = index.search(queryVector, k=top_k)

        result = []
        for idx in indices[0]:
            idx = int(idx)
            nodeText = G.nodes[idx]["text"]
            neighbors = list(G.successors(idx))
            print(neighbors)
            if neighbors:
                neighborText = [G.nodes[neighbors[n]]["text"] for n in neighbors]
                result.append(nodeText + " " + " ".join(neighborText))
            else:
                result.append(nodeText)
        return result
