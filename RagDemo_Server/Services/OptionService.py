import os
import ollama
from dotenv import load_dotenv
from DataModels.Models.Option import Option

load_dotenv()
_openAIKey = os.environ.get("AZURE_OPENAI_KEY")
_openAIEndpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")


class OptionService:
    def __init__(self) -> None:
        pass

    async def GetModelList(self) -> list[Option]:
        client = ollama.AsyncClient(host="http://host.docker.internal:11434")
        response = await client.list()  # returns a dict
        models = response["models"]  # list of dicts

        model_list: list[Option] = [
            Option(
                Value=model["model"],
                Label=model["model"].split(":")[0],  # strip tag for display
            )
            for model in models
        ]
        if _openAIKey and _openAIEndpoint:
            model_list.extend(
                [
                    Option(Value="gpt-4.1", Label="gpt-4.1"),
                    Option(Value="gpt-4.1-mini", Label="gpt-4.1-mini"),
                    Option(Value="gpt-4.1-nano", Label="gpt-4.1-nano"),
                ]
            )
        return model_list

    def GetDataList(self) -> list[str]:
        dataNameList: list[str] = [
            entry.name for entry in os.scandir("./VectorStore/") if entry.is_dir()
        ]
        return dataNameList
