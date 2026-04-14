import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { FormParams } from '@/type/formParams'
import { getDataNameList } from '@/api/server/Options'

export const useGobalStore = defineStore('global', () => {
  const isDrawerOpen = ref<boolean>(false)
  const formParams = ref<FormParams>({
    questions: [],
    systemMessage:
      'You are a helpful assistant that formats all responses in Markdown, with proper headings, lists, code blocks, and tables.Format the answer using headings, bullet points, tables when needed, and fenced code blocks with language identifiers. Use LaTeX for math if required.',
    model: null,
    mode: 1,
    dataList: [],
    finalPrompt:
      'You do not need repeat the question, and answer header. If no data you can anxwer "I do not know."',
  })
  const uploadedFile = ref<File | null>(null)
  const maxTokens = ref<number>(60)
  const splitTexts = ref<string[]>([])
  const dataName = ref<string>('')
  const dataList = ref<string[]>()

  function getDataList() {
    getDataNameList()
      .then((response: string[]) => {
        dataList.value = response
        if (formParams.value.dataList.length === 0 && response.length > 0) {
          formParams.value.dataList.push(response[0])
        }
      })
      .catch((error) => {
        console.error('Failed to fetch data list:', error)
      })
  }

  return {
    isDrawerOpen,
    formParams,
    splitTexts,
    maxTokens,
    uploadedFile,
    dataName,
    dataList,
    getDataList,
  }
})
