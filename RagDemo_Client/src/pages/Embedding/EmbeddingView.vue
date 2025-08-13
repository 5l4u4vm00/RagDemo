<script setup lang="ts">
import { ref } from 'vue'
import { useGobalStore } from '@/stores/global'
import { storeToRefs } from 'pinia'

const { splitTexts } = storeToRefs(useGobalStore())
</script>

<template>
  <div></div>
</template>
