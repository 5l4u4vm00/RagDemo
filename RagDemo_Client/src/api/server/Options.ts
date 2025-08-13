import server from '.'

export function getModelOptions() {
  return server({ url: 'Options/GetModelOptions', method: 'get' })
}

export function getDataNameList() {
  return server({ url: 'Options/GetDataNameList', method: 'get' })
}
