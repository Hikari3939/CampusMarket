<template>
  <router-view></router-view>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useUserStore } from './stores/user'
import { useChatStore } from './stores/chat'

const userStore = useUserStore()
const chatStore = useChatStore()

const handleStorageChange = (e) => {
  if (e.key === 'token') {
    window.location.reload()
  }
}

watch(() => userStore.token, (newToken) => {
  if (newToken) {
    chatStore.connectSocket()
  } else {
    chatStore.disconnectSocket()
  }
}, { immediate: true })

onMounted(() => {
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
})
</script>
