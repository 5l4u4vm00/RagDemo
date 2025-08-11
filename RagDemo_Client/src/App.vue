<script setup lang="ts">
import DrawerWidget from './components/DrawerWidget.vue'
import { useGobalStore } from './stores/global'
import { storeToRefs } from 'pinia'

const { isDrawerOpen } = storeToRefs(useGobalStore())
</script>

<template>
  <div class="flex flex-col h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <header
      class="p-4 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 flex items-center space-x-4"
    >
      <button
        @click="isDrawerOpen = !isDrawerOpen"
        class="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
      <h1 class="text-xl font-bold">ChatBot</h1>
    </header>

    <div class="relative flex-1 flex flex-row overflow-y-auto">
      <DrawerWidget :is-open="isDrawerOpen" @close="isDrawerOpen = false" />
      <div
        class="w-[100%] h-[100%] flex flex-col transition-all duration-300 overflow-y-auto"
        :class="{ 'ml-64': isDrawerOpen }"
      >
        <RouterView></RouterView>
      </div>
    </div>
  </div>
</template>
