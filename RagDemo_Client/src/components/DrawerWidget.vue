<script setup lang="ts">
import Cross from '@/assets/icon/cross.svg'
import Gear from '@/assets/icon/gear.svg'
import { getDataNameList } from '@/api/server/Options'
import { onMounted, ref } from 'vue'
import { useGobalStore } from '@/stores/global'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
})

const router = useRouter()
const { formParams, uploadedFile, dataName, dataList } = storeToRefs(useGobalStore())
const { getDataList } = useGobalStore()
const isSetting = ref<boolean>(false)

onMounted(() => {
  getDataList()
})

defineEmits(['close'])

function handleUpload() {
  // Create an input element dynamically
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.docx,.pdf' // specify allowed file types if needed

  input.onchange = async (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      uploadedFile.value = target.files[0]
      console.log('File selected:', uploadedFile.value.name)
      dataName.value = uploadedFile.value.name.split('.')[0]
      router.push('/Embedding')

      // Prepare FormData
      // const formData = new FormData()
      // formData.append('file', uploadedFile.value)
      //
      // splitTextFromDoc({ maxToken: 60 }, formData)
      //   .then((response: string[]) => {
      //     splitTexts.value = response
      //   })
      //   .catch((e) => {
      //     console.error(e)
      //   })
    }
  }

  input.click() // trigger file selection
}
</script>

<template>
  <div
    class="absolute flex flex-col h-full w-0 bg-white dark:bg-gray-800 shadow-lg transition-transform duration-300 transform"
    :class="{ '-translate-x-64': !isOpen, 'w-64': isOpen }"
  >
    <div
      class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between"
    >
      <h2 class="text-lg font-bold">DataBase</h2>
      <button
        @click="$emit('close')"
        class="p-1 rounded-xl hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <img :src="Cross" class="w-6 h-6" style="filter: brightness(0) invert(1)" />
      </button>
    </div>

    <div class="relative flex-1 p-4 overflow-y-auto space-y-4 vector">
      <div class="flex flex-col no-wrap gap-4" v-if="!isSetting">
        <label
          v-for="dataName in dataList"
          :key="dataName"
          class="flex items-center space-x-2 mb-1 cursor-pointer"
        >
          <input
            type="checkbox"
            :value="dataName"
            v-model="formParams.dataList"
            class="form-checkbox text-blue-500"
          />
          <span class="text-md">{{ dataName }}</span>
        </label>
      </div>
      <div v-else class="flex flex-col no-wrap gap-4 w-full">
        <label class="flex flex-col items-start space-y-2 mb-1">
          <span class="text-md">systemMessage :</span>
          <textarea
            v-model="formParams.systemMessage"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-sm form-checkbox text-white"
          ></textarea>
        </label>
        <label class="flex flex-col items-start space-y-2 mb-1">
          <span class="text-md">Params :</span>
          <textarea
            v-model="formParams.finalPrompt"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-sm form-checkbox text-white"
          >
          </textarea>
        </label>
        <button
          @click="
            () => {
              isSetting = false
            }
          "
          class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
        >
          Back
        </button>
      </div>
    </div>
    <div
      class="flex justify-between items-center p-4 border-t border-gray-200 dark:border-gray-700"
    >
      <button
        @click="
          () => {
            isSetting = true
          }
        "
        class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer flex items-center space-x-1"
      >
        <img :src="Gear" class="w-6 h-6" style="filter: brightness(0) invert(1)" />
      </button>

      <button
        @click="handleUpload"
        class="p-2 rounded-md dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer"
      >
        Upload File
      </button>
    </div>
  </div>
</template>
