<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  sender: {
    type: String,
    required: true,
    validator: (value) => ['user', 'gemini'].includes(value),
  },
})

// 根據發送者動態改變樣式
const messageClasses = computed(() => [
  'flex',
  {
    'justify-end': props.sender === 'user',
    'justify-start': props.sender === 'gemini',
  },
])

const bubbleClasses = computed(() => [
  'p-3 rounded-xl max-w-sm lg:max-w-md',
  {
    'bg-blue-600 text-white rounded-br-none': props.sender === 'user',
    'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-none':
      props.sender === 'gemini',
  },
])
</script>

<template>
  <div :class="messageClasses">
    <div :class="bubbleClasses">
      <p class="text-sm">
        {{ message }}
      </p>
    </div>
  </div>
</template>
