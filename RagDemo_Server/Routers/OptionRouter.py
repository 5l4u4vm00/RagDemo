from fastapi import APIRouter
from Services.OptionService import OptionService

router = APIRouter(prefix="/Options")
_service = OptionService()


@router.get("/GetModelOptions")
async def GetModelOptions():
    result = await _service.GetModelList()
    return result


@router.get("/GetDataNameList")
def GetDataNameList():
    result = _service.GetDataList()
    return result
