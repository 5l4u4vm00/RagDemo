# RagDemo - 全端 RAG 聊天應用程式

本專案是一個全端的「檢索增強生成」(Retrieval-Augmented Generation, RAG) 應用程式。它結合了 Vue.js 前端與 Python FastAPI 後端，打造一個能夠根據指定文件內容回答問題的智慧聊天助理。

此應用程式採用向量與圖譜檢索技術，以提供準確且符合上下文的回應。它支援多種文件格式，並可彈性設定使用本地端 (Ollama) 或遠端 (OpenAI) 的大型語言模型。

## 技術棧

- **前端:** Vue.js, Vite, Pinia, Tailwind CSS
- **後端:** Python, FastAPI, Ollama, OpenAI
- **向量儲存:** FAISS (用於高效的相似性搜尋)
- **資料處理:** NetworkX (用於圖譜檢索)
- **容器化:** Docker, Docker Compose

## 功能亮點

- **直觀的聊天介面:** 提供一個簡潔的網頁 UI，方便使用者互動。
- **基於文件的問答:** 從 `RagDemo_Server/documents` 目錄中的文件擷取資訊並生成答案。
- **支援多種文件格式:** 可處理 PDF (`.pdf`) 和 Microsoft Word (`.docx`) 檔案。
- **進階檢索策略:**
  - **向量搜尋:** 使用 `multilingual-e5-large` 模型進行快速的語意檢索。
  - **圖譜搜尋:** 建立知識圖譜以尋找具備上下文關聯的資訊。
- **彈性的 LLM 配置:** 同時支援透過 Ollama 運行的本地模型及 OpenAI API。
- **容器化部署:** 整個應用程式透過 Docker 管理，簡化了設定與部署流程。

## 開始使用

請使用 Docker 來運行此應用程式。
請啟動ollama服務

### 環境要求

- [Docker](https://www.docker.com/get-started) & [Docker Compose](https://docs.docker.com/compose/install/)
- 一組 Azure OpenAI API 金鑰與端點 (若要使用 OpenAI 模型)。

### 設定步驟

1. **複製儲存庫:**

   ```bash
   git clone <repository-url>
   cd RagDemo
   ```

2. **設定環境變數:**
   在 `RagDemo_Server` 目錄中建立一個名為 `.env` 的檔案，並填入您的 Azure OpenAI 憑證。即使您打算使用本地模型，此步驟也是必要的。

   ```env
   # RagDemo_Server/.env
   AZURE_OPENAI_KEY="您的-azure-openai-金鑰"
   AZURE_OPENAI_ENDPOINT="您的-azure-openai-端點"
   ```

### 運行應用程式

1. **使用 Docker Compose 啟動:**
   在專案根目錄下，執行以下指令：

   ```bash
   docker-compose up --build
   ```

2. **存取應用程式:**
   - **前端聊天介面:** `http://localhost:5173`
   - **後端 API 文件:** `http://localhost:8888/docs`

## 運作原理

1. **資料讀取:** 後端服務讀取文件，並將其文字內容分割成較小的區塊。
2. **向量嵌入:** 每個區塊都透過 OpenAI 模型轉換為向量嵌入。
3. **資料儲存:** 建立資料夾，嵌入向量儲存於 FAISS 索引檔 (`<資料名稱>.faiss`)，而原始文字區塊則存放在 `<資料名稱>.json`。
4. **圖譜建立:** 系統會根據語意相似度建立一個知識圖譜 (`<資料名稱>.graphml`)，用來對應文字區塊之間的關聯。
5. **檢索與生成:**
   - 使用者的問題會被轉換成一個向量。
   - FAISS 索引會找出最相關的文字區塊 (向量搜尋)。
   - 知識圖譜會被用來尋找與這些區塊相關的鄰近節點，以補充更多上下文 (圖譜搜尋)。
   - 檢索到的上下文與原始問題會被一同發送到設定好的 LLM (Ollama 或 OpenAI)。
   - LLM 會生成最終答案，並以串流方式回傳給使用者。
