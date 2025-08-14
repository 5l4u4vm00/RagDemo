import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/pages/Home/HomeView.vue'
import EmbeddingView from '@/pages/Embedding/EmbeddingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/Embedding',
      name: 'embedding',
      component: EmbeddingView,
    },
  ],
})

export default router
