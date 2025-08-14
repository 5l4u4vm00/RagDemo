import os
import ollama
import faiss
import json
import numpy as np
import networkx as nx
from dotenv import load_dotenv
from openai import AzureOpenAI
from ollama import ChatResponse
from openai.types.chat.completion_create_params import ChatCompletionMessageParam
from scipy.stats import f
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from torch import Tensor
from DataModels.Enums.EMode import EMode

load_dotenv()
_openAIKey = os.environ.get("AZURE_OPENAI_KEY")
_openAIEndpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
_dataCollectionPath = "./VectorStore/"
_faissPath = "./VectorStore/vectorDB.faiss"
_jsonPath = "./VectorStore/textList.json"
_nxPath = "./VectorStore/graphDB.graphml"

if _openAIKey and _openAIEndpoint:
    _openAIClient = AzureOpenAI(
        azure_endpoint=_openAIEndpoint,
        api_key=_openAIKey,
        api_version="2024-05-01-preview",
    )


class AIService:
    def __init__(self, model: str = "intfloat/multilingual-e5-large"):
        self._tokenizer = AutoTokenizer.from_pretrained(model)
        self._model = AutoModel.from_pretrained(model)

    async def AskLlama(
        self,
        user_input: str,
        systemMassage: str = "",
        model: str = "llama3",
        mode: EMode = EMode.vector,
        dataList: list[str] = [],
        finalPrompt: str = "",
    ) -> str | None:
        """
        Ask question to local model
        """
        client = ollama.AsyncClient(host="http://host.docker.internal:11434")

        prompts = self.SimilarQueryAndReturnPrompts(
            user_input, top_k=5, mode=mode, dataList=dataList, finalPrompt=finalPrompt
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": systemMassage}
        ]
        messages.append({"role": "user", "content": prompts})
        response: ChatResponse = await client.chat(model=model, messages=messages)
        return response.message.content

    def AskOpenAI(
        self,
        user_input: str,
        systemMassage: str = "",
        model: str = "gpt-4.1",
        mode: EMode = EMode.vector,
        dataList: list[str] = [],
        finalPrompt: str = "",
    ) -> str | None:
        """
        Ask question to openai model
        """
        if not _openAIClient:
            return "Please set the azure openai key and endpoint in .env"
        prompts = self.SimilarQueryAndReturnPrompts(
            user_input, top_k=2, mode=mode, dataList=dataList, finalPrompt=finalPrompt
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": systemMassage}
        ]
        messages.append({"role": "user", "content": prompts})
        response = _openAIClient.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content

    def SimilarQueryAndReturnPrompts(
        self,
        question: str,
        top_k: int = 5,
        mode: EMode = EMode.vector,
        dataList: list[str] = [],
        finalPrompt: str = "",
    ):
        match mode:
            case EMode.vector:
                contextChunks = self.SearchSimilar(question, top_k, dataList=dataList)
            case EMode.graph:
                contextChunks = self.SearchGraphRag(question, top_k, dataList=dataList)
        prompts = self.BuildPrompt(question, contextChunks, finalPrompt)
        return prompts

    @staticmethod
    def LoadVectorFile(filePath: str) -> faiss.Index:
        index = faiss.read_index(filePath)
        return index

    def SearchSimilar(self, question: str, top_k: int = 5, dataList: list[str] = []):
        texts: list[str] = []
        embeddings: list[list[float]] = []
        for dataName in dataList:
            folderPath = _dataCollectionPath + dataName
            jsonFile = open(folderPath + f"/{dataName}.json", "r")
            texts.extend(json.load(jsonFile))
            jsonFile.close()
            index = self.LoadVectorFile(folderPath + f"/{dataName}.faiss")
            ntotal, d = index.ntotal, index.d
            recons = np.zeros((ntotal, d), dtype="float32")
            embeddings.extend(index.reconstruct_n(0, ntotal, recons))

        index = self.CreateFaissIndex(embeddings)

        questionVector = np.array(self.EmbeddingTexts(texts=[question])).astype(
            "float32"
        )

        distances, indices = index.search(questionVector, k=top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            result_text = texts[idx]
            results.append(result_text)

        return results

    def SearchGraphRag(self, query: str, top_k=2, dataList: list[str] = []):
        embeddings: list[list[float]] = []
        G = nx.DiGraph()

        for dataName in dataList:
            folderPath = _dataCollectionPath + dataName
            index = self.LoadVectorFile(folderPath + f"/{dataName}.faiss")

            # --- Reconstruct embeddings ---
            ntotal, d = index.ntotal, index.d
            recons = np.zeros((ntotal, d), dtype="float32")
            index.reconstruct_n(0, ntotal, recons)
            embeddings.extend(recons.tolist())

            # --- Merge graph ---
            G1 = nx.read_graphml(folderPath + f"/{dataName}.graphml", node_type=int)

            if len(G.nodes) > 0:
                max_node = max(G.nodes)
            else:
                max_node = -1

            mapping = {n: n + max_node + 1 for n in G1.nodes()}  # keep as int
            G1 = nx.relabel_nodes(G1, mapping)
            G = nx.compose(G, G1)

        # --- Create combined FAISS index ---
        index = self.CreateFaissIndex(embeddings)

        # --- Query ---
        queryVector = np.array(self.EmbeddingTexts(texts=[query])).astype("float32")
        distances, indices = index.search(queryVector, k=top_k)

        result = []
        for idx in indices[0]:
            idx = int(idx)
            nodeText = G.nodes[idx]["text"]
            neighbors = list(G.successors(idx))
            if neighbors:
                neighborText = [G.nodes[n]["text"] for n in neighbors]
                result.append(nodeText + " " + " ".join(neighborText))
            else:
                result.append(nodeText)

        return result

    @staticmethod
    def CreateFaissIndex(embeddings: list[list[float]]):
        dim = len(embeddings[0])
        index = faiss.IndexFlatL2(dim)

        npEmbeddings = np.array(embeddings).astype("float32")
        index.add(npEmbeddings)
        return index

    @staticmethod
    def BuildPrompt(question: str, context_chunks: list[str], finalPrompt: str) -> str:
        context_text = "\n\n".join(context_chunks)
        prompt = f"""
        nswer the questions based on the following information：
        {context_text}
        question：{question}
        f{finalPrompt}
        """
        return prompt

    def EmbeddingTexts(self, texts: list[str]) -> list[list[float]]:
        inputs = self._tokenizer(
            texts, padding=True, max_length=512, truncation=True, return_tensors="pt"
        )
        outputs = self._model(**inputs)
        embeddings = self.AveragePool(
            outputs.last_hidden_state, inputs["attention_mask"]
        )
        embeddings = F.normalize(embeddings, p=2, dim=1).tolist()
        return embeddings

    @staticmethod
    def AveragePool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
