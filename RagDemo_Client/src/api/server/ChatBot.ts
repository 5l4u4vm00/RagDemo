import server from '.'

export function askLLaMA(data: Object) {
  return server({ url: '/ChatBot/AskLLaMA', method: 'post', data })
}

export function askOpenAI(data: Object) {
  return server({ url: '/ChatBot/AskOpenAI', method: 'post', data })
}
