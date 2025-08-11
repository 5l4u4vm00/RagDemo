from fastapi import APIRouter
from DataModels.Request import Request
from Services.AIService import AIService

router = APIRouter(prefix="/ChatBot")
_aiHelper = AIService()


@router.post("/AskLLaMA")
async def AskLlama(request: Request) -> str | None:
    """
    Sends a question to the LLaMA model and returns the response.

    Parameters:
    - request (Request): Contains the user question.

    Returns:
    - str | None: The model's response, or None if the request fails.
    """
    result = await _aiHelper.AskLlama(user_input=request.question)

    return result


@router.post("/AskOpenAI")
def AskOpenAI(request: Request):
    """
    Sends a question to the OpenAI model and returns the response.

    Parameters:
    - request (Request): Contains the user question.

    Returns:
    - str | None: The model's response, or None if the request fails.
    """
    result = _aiHelper.AskOpenAI(user_input=request.question)

    return result


@router.get("/embeddingFromFolder")
def EmbeddingFromFile():
    chunks = _aiHelper.EmbeddingFileInFolder()
    return chunks
