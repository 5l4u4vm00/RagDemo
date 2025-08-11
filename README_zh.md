# RagDemo - 全端 RAG 聊天應用程式

本專案是一個全端檢索增強生成 (Retrieval-Augmented Generation, RAG) 應用程式，可作為您的智能助理。它包含一個 Vue.js 前端和一個 FastAPI 後端，讓使用者能夠根據提供的文件集合進行提問並獲得回答。

此應用程式利用向量和圖譜檢索等先進技術，以提供準確且具備上下文感知的回應。它支援多種文件格式，並可設定使用本地 (Ollama) 或遠端 (OpenAI) 的大型語言模型。

## 系統架構

此應用程式由兩個主要服務組成，並透過 Docker Compose 進行協調：

-   **`RagDemo_Client` (前端):** 一個使用 Vue.js 建置的網頁聊天介面。它與後端 API 通訊，以傳送問題並顯示回應。
-   **`RagDeom_Server` (後端):** 一個使用 Python 和 FastAPI 建置的 API。它負責處理文件、生成嵌入向量，並與 LLM 互動以生成答案。

## 功能

-   **網頁介面:** 提供直觀的聊天介面與助理互動。
-   **基於文件的問答:** 根據 `RagDeom_Server/documents` 目錄中儲存的文件內容回答問題。
-   **支援多種文件格式:** 可處理 PDF (`.pdf`) 和 Microsoft Word (`.docx`) 檔案。
-   **基於向量的檢索:** 利用 OpenAI 的 `text-embedding-3-small` 模型進行高效的相似性搜尋。
-   **基於圖譜的檢索:** 建立相關文字區塊的知識圖譜，以提供更具上下文關聯性的資訊。
-   **FAISS 向量儲存:** 將向量嵌入儲存在 FAISS 索引中，以實現快速檢索。
-   **支援雙 LLM:** 可靈活設定使用本地的 LLaMA 模型 (透過 Ollama) 或 OpenAI API。
-   **容器化:** 使用 Docker 和 Docker Compose 輕鬆運行整個應用程式。

## 開始使用

建議使用 Docker 來運行此應用程式。

### 先決條件

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)
-   一個 Azure OpenAI API 金鑰和端點 (若要使用 OpenAI 模型)。

### 設定步驟

1.  **複製儲存庫：**
    ```bash
    git clone <repository-url>
    cd RagDemo
    ```

2.  **新增文件:**
    將您想作為知識庫的 PDF 和 DOCX 檔案放入 `RagDeom_Server/documents/` 目錄中。

3.  **設定環境變數:**
    在 `RagDeom_Server` 目錄中建立一個名為 `.env` 的檔案，並新增您的 Azure OpenAI 憑證。即使您計劃使用本地模型，此步驟也是必要的。

    ```
    # RagDeom_Server/.env
    AZURE_OPENAI_KEY="your-azure-openai-key"
    AZURE_OPENAI_ENDPOINT="your-azure-openai-endpoint"
    ```

### 執行應用程式

1.  **使用 Docker Compose 啟動:**
    在專案的根目錄中開啟一個終端機，並執行：
    ```bash
    docker-compose up --build
    ```
    首次啟動時，後端服務將自動讀取文件、建立向量嵌入並建構知識圖譜。這可能需要一些時間，具體取決於您文件的數量和大小。

2.  **存取應用程式:**
    -   **前端聊天介面:** 開啟您的網頁瀏覽器並前往 `http://localhost:5173`。
    -   **後端 API 文件:** 後端 API 文件可在 `http://localhost:8888/docs` 查閱。

## 手動設定 (開發用途)

在開發過程中，您可以分別運行前端和後端服務。詳細說明請參閱 `RagDemo_Client` 和 `RagDeom_Server` 目錄中的 README 檔案。

## 運作方式

1.  **文件處理:** 後端會從 `documents` 目錄中的 PDF 和 DOCX 檔案讀取文字，並將其分割成較小的區塊。
2.  **向量嵌入:** 每個文字區塊都會使用 OpenAI 的 `text-embedding-3-small` 模型轉換為向量嵌入。
3.  **向量儲存:** 嵌入向量儲存在 FAISS 索引 (`vectorDB.faiss`) 中，而對應的文字區塊則儲存在 `textList.json` 中。
4.  **圖譜建立:** 系統會建立一個知識圖譜 (`graphDB.graphml`)，其中節點是文字區塊，而邊則連接具有高餘弦相似度的區塊，以捕捉它們之間的關係。
5.  **問答流程:**
    -   當使用者透過前端提出問題時，問題會被傳送到後端 API。
    -   後端會為問題建立一個向量嵌入，並使用 FAISS 索引找出最相似的文字區塊。
    -   接著，它會遍歷知識圖譜以檢索相鄰的區塊，從而獲得額外的上下文。
    -   這個上下文會與原始問題一起被格式化成一個提示 (prompt)。
    -   最後，該提示會被傳送到設定好的 LLM (Ollama 或 OpenAI) 以生成回應，並將其串流回傳給使用者。