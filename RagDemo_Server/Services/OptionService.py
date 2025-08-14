import os
import ollama
from DataModels.Models.Option import Option


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
        return model_list

    def GetDataList(self) -> list[str]:
        dataNameList: list[str] = [
            entry.name for entry in os.scandir("./VectorStore/") if entry.is_dir()
        ]
        return dataNameList
