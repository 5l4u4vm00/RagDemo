import os
import ollama
from dotenv import load_dotenv
from DataModels.Models.Option import Option
from Database.db import get_conn

load_dotenv()
_openAIKey = os.environ.get("AZURE_OPENAI_KEY")
_openAIEndpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
_ollamaHost = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")


class OptionService:
    def __init__(self) -> None:
        pass

    async def GetModelList(self) -> list[Option]:
        model_list: list[Option] = []
        if _openAIKey and _openAIEndpoint:
            model_list.extend(
                [
                    Option(Value="gpt-4.1", Label="gpt-4.1"),
                    Option(Value="gpt-4.1-mini", Label="gpt-4.1-mini"),
                    Option(Value="gpt-4.1-nano", Label="gpt-4.1-nano"),
                ]
            )
        try:
            client = ollama.AsyncClient(host=_ollamaHost)
            response = await client.list()  # returns a dict
            models = response["models"]  # list of dicts

            model_list.extend(
                [
                    Option(
                        Value=model["model"],
                        Label=model["model"].split(":")[0],  # strip tag for display
                    )
                    for model in models
                ]
            )
            return model_list
        except Exception as e:
            print(f"[GetModelList] ollama error: {e!r} host={_ollamaHost}")
            return model_list

    def GetDataList(self) -> list[str]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name FROM datasets ORDER BY name;")
                return [row[0] for row in cur.fetchall()]
