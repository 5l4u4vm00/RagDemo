import axios from 'axios'

// 建立一個 axios 實例
const service = axios.create({
  // 設置 API 基礎 URL
  // 在開發環境中，這可以指向你的後端 API
  // 在生產環境中，你可以改為部署後的 API 網址
  // 也可以在 vite.config.js 中設定 proxy
  baseURL: import.meta.env.VITE_API_URL,

  // 設置請求逾時時間，例如 10 秒
  timeout: 40000,

  // 設置請求頭，例如 Content-Type
  headers: {
    'Content-Type': 'application/json',
  },
})

// 請求攔截器 (Request Interceptors)
// 在發送請求之前做些事情，例如在每個請求中帶上 Token
service.interceptors.request.use(
  (config) => {
    // 假設你的 Token 存在於 localStorage 中
    const token = localStorage.getItem('accessToken')
    if (token) {
      // 在請求頭中加入 Authorization
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    // 處理請求錯誤
    console.error('Request Error:', error)
    return Promise.reject(error)
  },
)

// 回應攔截器 (Response Interceptors)
// 在收到回應之後做些事情，例如統一處理錯誤碼
service.interceptors.response.use(
  (response) => {
    // 如果狀態碼是 200，直接返回數據
    const res = response.data
    if (response.status === 200) {
      return res
    }
    // 其他非 200 狀態碼，可以根據後端 API 規範處理
    return Promise.reject(new Error(res.message || 'Error'))
  },
  (error) => {
    // 處理 HTTP 狀態碼錯誤，例如 401, 403, 404, 500 等
    console.error('Response Error:', error.response)
    const { status, data } = error.response

    switch (status) {
      case 401:
        // 處理未授權錯誤，例如導向登入頁面
        console.error('Unauthorized, please log in again.')
        // router.push('/login'); // 假設你有 Vue Router
        break
      case 403:
        // 處理禁止訪問錯誤
        console.error('Forbidden, you do not have permission.')
        break
      case 404:
        // 處理找不到資源錯誤
        console.error('Resource not found.')
        break
      case 500:
        // 處理伺服器內部錯誤
        console.error('Server Internal Error.')
        break
      default:
        console.error(`Unhandled error with status code ${status}`)
    }
    return Promise.reject(error)
  },
)

// 導出封裝好的 axios 實例
export default service
