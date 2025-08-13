import type { AxiosPromise } from 'axios'
import server from '.'

export function splitTextFromDoc(params: Object, data: Object): Promise<AxiosPromise<string[]>> {
  return server({
    url: '/Pretarget/SplitTextFromDoc',
    method: 'post',
    data,
    params,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function embeddingChunksStore(data: Object) {
  return server({ url: '/Pretarget/EmbeddingChunksStore', method: 'post', data })
}
