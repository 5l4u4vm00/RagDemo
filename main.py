from fastapi import FastAPI
from Routers.chatRouter import router as chatRouter

app = FastAPI(title="我的智能助理", version="v1")
app.include_router(chatRouter, tags=["chatBot"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8888, reload=True)
