export interface FormParams {
  questions: object[]
  systemMessage: string
  model: string | null
  mode: number | null
  dataList: string[]
  finalPrompt: string
}
