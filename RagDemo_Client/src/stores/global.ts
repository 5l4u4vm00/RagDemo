import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { FormParams } from '@/type/formParams'
import { getDataNameList } from '@/api/server/Options'

export const useGobalStore = defineStore('global', () => {
  const isDrawerOpen = ref<boolean>(false)
  const formParams = ref<FormParams>({
    question: '',
    systemMessage: '你是一個市民的好幫手,請使用繁體中文回答',
    model: null,
    mode: 1,
    dataList: [],
    finalPrompt: '回答不需使用根據,若無資料可回答"不知道"',
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
        formParams.value.dataList.push(dataList.value[0])
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
