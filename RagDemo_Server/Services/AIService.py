import os
import ollama
import faiss
import numpy as np
import networkx as nx
from dotenv import load_dotenv
from openai import AzureOpenAI
from ollama import ChatResponse
from openai.types.chat.completion_create_params import ChatCompletionMessageParam
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
from torch import Tensor
from DataModels.Enums.EMode import EMode
from Database.db import get_conn

load_dotenv()
_openAIKey = os.environ.get("AZURE_OPENAI_KEY")
_openAIEndpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
_ollamaHost = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")

if _openAIKey and _openAIEndpoint:
    _openAIClient = AzureOpenAI(
        azure_endpoint=_openAIEndpoint,
        api_key=_openAIKey,
        api_version="2024-05-01-preview",
    )


class AIService:
    def __init__(self, model: str = "intfloat/multilingual-e5-small"):
        self._tokenizer = AutoTokenizer.from_pretrained(model)
        self._model = AutoModel.from_pretrained(model)

    async def AskLlama(
        self,
        inputs: list[ChatCompletionMessageParam],
        systemMassage: str = "",
        model: str = "llama3",
        mode: EMode = EMode.vector,
        dataList: list[str] = [],
        finalPrompt: str = "",
    ) -> str | None:
        """
        Ask question to local model
        """
        client = ollama.AsyncClient(host=_ollamaHost)

        last_input = inputs.pop()["content"]
        prompts = self.SimilarQueryAndReturnPrompts(
            last_input,
            top_k=5,
            mode=mode,
            dataList=dataList,
            finalPrompt=finalPrompt,
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": systemMassage}
        ]
        messages.extend(inputs)
        messages.append({"role": "user", "content": prompts})
        response: ChatResponse = await client.chat(model=model, messages=messages)
        return response.message.content

    def AskOpenAI(
        self,
        inputs: list[ChatCompletionMessageParam],
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

        last_input = inputs.pop()["content"]
        prompts = self.SimilarQueryAndReturnPrompts(
            last_input,
            top_k=5,
            mode=mode,
            dataList=dataList,
            finalPrompt=finalPrompt,
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": systemMassage}
        ]
        messages.extend(inputs)
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

    def SearchSimilar(self, question: str, top_k: int = 5, dataList: list[str] = []):
        texts: list[str] = []
        embeddings: list[list[float]] = []

        with get_conn() as conn:
            with conn.cursor() as cur:
                for dataName in dataList:
                    cur.execute(
                        """
                        SELECT c.text, c.embedding
                        FROM chunks c
                        JOIN datasets d ON d.id = c.dataset_id
                        WHERE d.name = %s
                        ORDER BY c.chunk_idx;
                        """,
                        (dataName,),
                    )
                    for text, emb_str in cur.fetchall():
                        texts.append(text)
                        embeddings.append(
                            [float(x) for x in emb_str.strip("[]").split(",")]
                        )

        if not embeddings:
            return []

        index = self.CreateFaissIndex(embeddings)
        questionVector = np.array(self.EmbeddingTexts(texts=[question])).astype(
            "float32"
        )
        distances, indices = index.search(questionVector, k=top_k)

        return [texts[idx] for idx in indices[0]]

    def SearchGraphRag(self, query: str, top_k=2, dataList: list[str] = []):
        embeddings: list[list[float]] = []
        G = nx.DiGraph()

        with get_conn() as conn:
            with conn.cursor() as cur:
                global_offset = 0
                for dataName in dataList:
                    cur.execute(
                        """
                        SELECT c.chunk_idx, c.text, c.embedding
                        FROM chunks c
                        JOIN datasets d ON d.id = c.dataset_id
                        WHERE d.name = %s
                        ORDER BY c.chunk_idx;
                        """,
                        (dataName,),
                    )
                    chunk_rows = cur.fetchall()

                    for local_idx, text, emb_str in chunk_rows:
                        global_node = local_idx + global_offset
                        embeddings.append(
                            [float(x) for x in emb_str.strip("[]").split(",")]
                        )
                        G.add_node(global_node, text=text)

                    cur.execute(
                        """
                        SELECT e.src_idx, e.dst_idx, e.weight
                        FROM chunk_edges e
                        JOIN datasets d ON d.id = e.dataset_id
                        WHERE d.name = %s;
                        """,
                        (dataName,),
                    )
                    for src, dst, weight in cur.fetchall():
                        G.add_edge(
                            src + global_offset,
                            dst + global_offset,
                            weight=weight,
                        )

                    global_offset += len(chunk_rows)

        if not embeddings:
            return []

        index = self.CreateFaissIndex(embeddings)
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
