<script setup lang="ts">
defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

defineEmits(['close'])
</script>

<template>
  <div
    class="absolute flex flex-col h-full w-0 bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 transform"
    :class="{ '-translate-x-64': !isOpen, 'w-64': isOpen }"
  >
    <div
      class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between"
    >
      <h2 class="text-lg font-bold">歷史記錄</h2>
      <button
        @click="$emit('close')"
        class="p-1 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>

    <div class="relative flex-1 p-4 overflow-y-auto space-y-2">
      <div
        class="p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
      >
        <p class="text-sm font-semibold">對話一</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 truncate">這是第一段對話的簡短摘要...</p>
      </div>
      <div
        class="p-3 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
      >
        <p class="text-sm font-semibold">關於 Vue 的問題</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
          使用者詢問了 Vue 3 的 Composition API...
        </p>
      </div>
    </div>
    <div class="flex justify-end p-4">
      <button
        class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
      >
        上傳檔案
      </button>
    </div>
  </div>
</template>
