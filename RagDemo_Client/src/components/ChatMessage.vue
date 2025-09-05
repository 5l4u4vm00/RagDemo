<script setup lang="ts">
import { marked } from '@/boot/marked'
import { computed } from 'vue'

const rendered = computed(() => {
  if (props.sender !== 'user') {
    return marked.parse(props.message || '')
  } else {
    return null
  }
})

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
    <article class="markdown-body" v-if="rendered" v-html="rendered"></article>
    <div
      class="p-3"
      v-else
      :class="{
        'bg-blue-600 text-white rounded-br-none  rounded-xl max-w-sm lg:max-w-md':
          props.sender === 'user',
      }"
    >
      <p class="text-sm">
        {{ message }}
      </p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.markdown-body {
  box-sizing: border-box;
  padding: 1rem;
  background-color: inherit;
}

@media (max-width: 767px) {
  .markdown-body {
    padding: 15px;
  }
}
</style>
