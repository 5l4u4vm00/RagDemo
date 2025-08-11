import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useGobalStore = defineStore('global', () => {
  const isDrawerOpen = ref(false)

  return { isDrawerOpen }
})
