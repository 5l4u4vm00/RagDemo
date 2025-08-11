from fastapi import APIRouter, UploadFile, File
from Services.PreTargetService import PreTargetService

router = APIRouter(prefix="/Pretarget")

_service = PreTargetService()


@router.post("/SplitTextFromDoc")
async def SplitTextFromDoc(file: UploadFile = File(), maxToken: int = 60) -> list[str]:
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
def EmbeddingChunkTextsStore(chunks:list[str]):
