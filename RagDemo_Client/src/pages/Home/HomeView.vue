<script setup>
import { ref, nextTick, watch, onMounted } from 'vue'
import ChatMessage from '@/components/ChatMessage.vue'
import { askLLaMA } from '@/api/server/ChatBot'
import { getModelOptions } from '@/api/server/Options'
import { useGobalStore } from '@/stores/global'
import { storeToRefs } from 'pinia'

const { formParams } = storeToRefs(useGobalStore())
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const modelList = ref([])

async function sendMessage() {
  if (inputMessage.value.trim() === '') return
  if (!isLoading.value) {
    messages.value.push({ sender: 'user', text: inputMessage.value })
    formParams.value.question = inputMessage.value
    inputMessage.value = ''

    isLoading.value = true
    try {
      const response = await askLLaMA(formParams.value)
      isLoading.value = false
      messages.value.push({ sender: 'gemini', text: response })
    } catch (e) {
      messages.value.push({ sender: 'gemini', text: 'Error' })
    }
    isLoading.value = false
  }
}

onMounted(() => {
  getModelOptions().then((response) => {
    modelList.value = response
    formParams.value.model = response[2].Value
  })
})
</script>

<template>
  <div class="flex-1 flex justify-center overflow-y-auto">
    <div ref="chatContainer" class="w-[60%] p-4 overflow-y-auto flex flex-col gap-4 no-scrollbar">
      <ChatMessage
        v-for="(message, index) in messages"
        :key="index"
        :message="message.text"
        :sender="message.sender"
      />
      <div v-if="isLoading" class="flex justify-start">
        <div class="p-3 rounded-xl bg-gray-700 text-gray-100 rounded-bl-none">
          <img src="@/assets/loading.gif" alt="Gemini is thinking" class="h-6 w-auto" />
        </div>
      </div>
    </div>
  </div>
  <div class="flex justify-center">
    <form
      @submit.prevent="sendMessage"
      class="p-4 bg-white w-[60%] rounded-lg mb-6 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="flex space-x-2">
        <select
          v-model="formParams.mode"
          class="p-3 rounded-lg bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option :value="1">VectorRag</option>
          <option :value="2">GraphRag</option>
        </select>
        <select
          v-model="formParams.model"
          class="p-3 rounded-lg bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option v-for="model in modelList" :value="model.Value">{{ model.Label }}</option>
        </select>
        <input
          type="text"
          v-model="inputMessage"
          placeholder="Enter message..."
          class="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-gray-700"
        />
        <button
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          v-if="!isLoading"
        >
          Submit
        </button>
        <div
          type="submit"
          class="px-4 py-2 bg-gray-600 text-white font-semibold rounded-lg flex items-center"
          v-else
        >
          Submit
        </div>
      </div>
    </form>
  </div>
</template>
