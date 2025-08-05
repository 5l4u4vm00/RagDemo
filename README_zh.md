
# 我的智慧助理

這個專案是一個 RAG (Retrieval-Augmented Generation) 應用程式，它能作為一個智慧助理。它可以根據您提供的一系列文件來回答問題。該應用程式使用 FastAPI 框架建立，並利用本地和遠端的語言模型 (LLM) 來生成回應。

## 功能

- **基於文件的問答：** 根據儲存在 `documents` 目錄中的文件內容回答問題。
- **支援多種文件格式：** 可以處理 PDF (.pdf) 和 Microsoft Word (.docx) 檔案。
- **基於向量的檢索：** 利用 OpenAI 的 `text-embedding-3-small` 模型來建立文件文字的向量嵌入，從而實現高效的相似性搜尋。
- **FAISS 向量儲存：** 將向量嵌入儲存在 [FAISS](https://github.com/facebookresearch/faiss) 索引中，以便快速檢索。
- **支援雙 LLM：** 提供靈活性，可選擇使用本地的 LLaMA 模型 (透過 Ollama) 或 OpenAI API 來生成答案。
- **易於使用的 API：** 提供簡單的 API，用於提問和觸發文件嵌入過程。

## 專案結構

```
├── DataModels
│   └── Request.py
├── documents
│   └── (您的文件放在這裡)
├── Routers
│   └── chatRouter.py
├── Services
│   └── AIService.py
├── VectorStore
│   ├── textList.json
│   └── vectorDB.faiss
├── main.py
├── requirement.txt
└── README.md
```

## 開始使用

### 先決條件

- Python 3.7+
- UV 專案管理器
- 一個 Azure OpenAI API 金鑰和端點
- (可選) 已安裝並正在運行的 [Ollama](https://ollama.ai/)，以支援本地 LLM

### 安裝

1. **克隆儲存庫：**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **建立並啟用虛擬環境：**

   ```bash
   uv venv
   source .venv/bin/activate  # 在 Windows 上，請使用 `.venv\Scripts\activate`
   ```

3. **安裝相依套件：**

   ```bash
   uv add -r requirement.txt
   ```

4. **設定您的環境變數：**

   在專案的根目錄中建立一個 `.env` 檔案，並加入您的 Azure OpenAI 憑證：

   ```
   AZURE_OPENAI_KEY="your-azure-openai-key"
   AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
   ```

### 使用方式

1. **加入您的文件：**

   將您想作為知識庫的 PDF 和 DOCX 檔案放入 `documents` 目錄中。

2. **生成向量嵌入：**

   啟動應用程式，它將自動為 `documents` 資料夾中的文件觸發嵌入過程。

3. **執行應用程式：**

   ```bash
   uv run ./main.py
   ```

4. **存取 API：**

   API 文件將在 `http://127.0.0.1:8888/docs` 上提供。

## API 端點

- **`POST /ChatBot/AskLLaMA`**：將問題傳送至本地的 LLaMA 模型並回傳回應。

  **請求主體：**

  ```json
  {
    "question": "您的問題"
  }
  ```

- **`POST /ChatBot/AskOpenAI`**：將問題傳送至 OpenAI 模型並回傳回應。

  **請求主體：**

  ```json
  {
    "question": "您的問題"
  }
  ```

- **`GET /ChatBot/embeddingFromFolder`**：觸發讀取 `documents` 資料夾中的文件、建立向量嵌入並將其儲存在向量資料庫中的過程。

## 運作方式

1. **文件載入和分塊：** 應用程式會從 `documents` 目錄中的 PDF 和 DOCX 檔案讀取文字。然後使用 `tiktoken` 將文字分割成較小的區塊。

2. **向量嵌入：** 每個文字區塊都會使用 OpenAI 的 `text-embedding-3-small` 模型轉換為向量嵌入。

3. **向量儲存：** 向量嵌入儲存在 FAISS 索引 (`vectorDB.faiss`) 中，而對應的文字區塊則儲存在 JSON 檔案 (`textList.json`) 中。

4. **問答：**
   - 當收到問題時，應用程式會為問題建立一個向量嵌入。
   - 然後，它會使用 FAISS 索引來尋找文件中最相似的文字區塊。
   - 這些相關的文字區塊會與原始問題結合，形成一個提示 (prompt)。
   - 最後，該提示會被傳送至本地的 LLaMA 模型或 OpenAI API 以生成回應。
