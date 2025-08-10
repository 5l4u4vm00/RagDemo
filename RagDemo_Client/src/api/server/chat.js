import server from '.'

export function askLLaMA(data) {
  return server({ url: '/ChatBot/AskLLaMA', method: 'post', data })
}
