from fastapi import APIRouter, UploadFile, File
from Services.PreTargetService import PreTargetService

router = APIRouter(prefix="/Pretarget")

_service = PreTargetService()


@router.post("/SplitTextFromDoc")
async def SplitTextFromDoc(file: UploadFile = File(), maxToken: int = 100) -> list[str]:
    """
    Read and split text content from an uploaded .docx or .pdf file into token-sized chunks.

    Params:
    - maxToken (int): Maximum number of tokens per chunk (default is 100).

    FormBody:
    - file (UploadFile): The uploaded file to process (.docx or .pdf).

    Returns:
    - list[str]: A list of text chunks decoded from token slices.
    """
    result = await _service.SplitText(file, maxToken)
    return result


@router.post("/EmbeddingChunksStore")
def EmbeddingChunkTextsStore(chunks: list[str], dataName: str):
    """
    Processes a list of texts by first tokenizing them, then generating embeddings,
    and finally storing these embeddings along with the original texts and a graph representation.

    Args:
        texts (list[str]): The list of text strings to be processed.
        dataName (str): The name to be used for the output folder and files.
    """
    try:
        _service.EmbeddingTexts(chunks, dataName)
        return "Success"
    except Exception as e:
        return "Fail"
