<script setup>
import { ref, nextTick, watch } from 'vue'
import ChatMessage from '@/components/ChatMessage.vue'
import { askLLaMA } from '@/api/server/chat'

const messages = ref([])
const inputMessage = ref('')
const selectedMode = ref('vector')
const isLoading = ref(false)

async function sendMessage() {
  if (inputMessage.value.trim() === '') return
  if (!isLoading.value) {
    messages.value.push({ sender: 'user', text: inputMessage.value })
    const userMessage = inputMessage.value
    inputMessage.value = ''

    isLoading.value = true
    const response = await askLLaMA({ question: userMessage })
    isLoading.value = false

    messages.value.push({ sender: 'gemini', text: response })
  }
}

watch(
  messages,
  async () => {
    await nextTick()
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  },
  { deep: true },
)
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
          v-model="selectedMode"
          class="p-3 rounded-lg bg-gray-700 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="vector">VectorRag</option>
          <option value="graph">GraphRag</option>
        </select>
        <input
          type="text"
          v-model="inputMessage"
          placeholder="輸入訊息..."
          class="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50 dark:bg-gray-700"
        />
        <button
          type="submit"
          class="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          v-if="!isLoading"
        >
          送出
        </button>
        <div
          type="submit"
          class="px-4 py-2 bg-gray-600 text-white font-semibold rounded-lg flex items-center"
          v-else
        >
          送出
        </div>
      </div>
    </form>
  </div>
</template>
