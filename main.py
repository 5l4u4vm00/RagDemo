from fastapi import FastAPI
from Routers.chatRouter import router as chatRouter
from Routers.PreTargetRouter import router as PreTargetRouter

app = FastAPI(title="RagTool", version="v1")
app.include_router(chatRouter, tags=["chatBot"])
app.include_router(PreTargetRouter, tags=["preTarget"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)
