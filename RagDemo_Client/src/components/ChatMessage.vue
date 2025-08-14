<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps({
  message: {
    type: String,
    required: true,
  },
  sender: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div
    class="flex flex-col gap-y-1"
    :class="{ 'items-end': sender == 'user', 'items-start': sender != 'user' }"
  >
    <p class="text-sm">
      {{ sender }}
    </p>
    <div
      class="p-3 rounded-xl max-w-sm lg:max-w-md"
      :class="{
        'bg-blue-600 text-white rounded-br-none': props.sender === 'user',
        'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-bl-none':
          props.sender !== 'user',
      }"
    >
      <p class="text-sm">
        {{ message }}
      </p>
    </div>
  </div>
</template>
