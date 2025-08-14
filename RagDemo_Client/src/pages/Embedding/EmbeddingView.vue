<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useGobalStore } from '@/stores/global'
import { storeToRefs } from 'pinia'
import { splitTextFromDoc, embeddingChunksStore } from '@/api/server/PreTarget'
import { ref } from 'vue'

const router = useRouter()
const { splitTexts, maxTokens, uploadedFile, dataName } = storeToRefs(useGobalStore())
const { getDataList } = useGobalStore()
const isLoading = ref(false)

function previousStep() {
  splitTexts.value = []
}

function cancel() {
  uploadedFile.value = null
  maxTokens.value = 60
  splitTexts.value = []
  router.push('/')
}

function removeTexts(index: number) {
  splitTexts.value.splice(index, 1)
}

async function confirm() {
  try {
    isLoading.value = true
    if (!splitTexts.value.length) {
      const formData = new FormData()
      formData.append('file', uploadedFile.value as File)

      const response: string[] = await splitTextFromDoc({ maxToken: maxTokens.value }, formData)
      splitTexts.value = response
    } else {
      await embeddingChunksStore({ dataName: dataName.value }, splitTexts.value)
      getDataList()
      router.push('/')
    }
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="w-full h-full flex flex-col items-center overflow-y-auto p-4">
    <!-- Spinner while loading -->
    <div v-if="isLoading" class="flex items-center justify-center w-full h-full">
      <div
        class="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"
      ></div>
    </div>

    <template v-else>
      <div v-if="!splitTexts.length" class="w-[60%] flex-1 flex flex-col gap-y-2 items-start p-4">
        <label class="flex items-start space-x-4 mb-1 cursor-pointer">
          <span class="text-xl">maxTokens</span>
          <input
            v-model="maxTokens"
            type="number"
            max="512"
            min="10"
            class="p-2 border border-gray-300 dark:border-gray-600 rounded-sm form-checkbox text-white"
          />
        </label>
        <label class="flex items-start space-x-4 mb-1 cursor-pointer">
          <span class="text-xl">file name</span>
          <div class="p-2 border border-gray-300 dark:border-gray-600 rounded-sm text-white">
            {{ uploadedFile?.name }}
          </div>
        </label>
      </div>

      <div v-else class="w-[60%] flex-1 flex flex-col gap-y-2 items-start p-4">
        <label class="flex items-center space-x-4 mb-1 cursor-pointer">
          <span class="text-xl">data name</span>
          <input
            v-model="dataName"
            type="text"
            class="p-2 flex-1 border border-gray-300 dark:border-gray-600 rounded-sm form-checkbox text-white"
          />
        </label>
        <div class="w-full flex flex-row gap-x-1" v-for="(text, index) in splitTexts" :key="index">
          <input
            v-model="splitTexts[index]"
            type="text"
            class="p-2 flex-1 border border-gray-300 dark:border-gray-600 rounded-sm form-checkbox text-white"
          />
          <button
            @click="removeTexts(index)"
            class="p-2 rounded-md dark:bg-red-700 hover:bg-red-100 dark:hover:bg-red-600 cursor-pointer"
          >
            remove
          </button>
        </div>
      </div>

      <div class="flex flex-row space-x-4 mt-4">
        <button
          @click="cancel"
          :disabled="isLoading"
          class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
        >
          Cancel
        </button>
        <button
          v-if="splitTexts.length"
          @click="previousStep"
          :disabled="isLoading"
          class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
        >
          Previous step
        </button>
        <button
          @click="confirm"
          :disabled="isLoading"
          class="p-2 rounded-md dark:bg-blue-700 hover:bg-blue-100 dark:hover:bg-blue-600 cursor-pointer"
        >
          Confirm
        </button>
      </div>
    </template>
  </div>
</template>
