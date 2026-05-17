<template>
  <router-view></router-view>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useUserStore } from './stores/user'
import { useChatStore } from './stores/chat'

const userStore = useUserStore()
const chatStore = useChatStore()

// 监听其他标签页的 localStorage 变化
const handleStorageChange = (e) => {
  // 当 localStorage 中的 token 被其他标签页修改或删除时
  if (e.key === 'token') {
    console.warn('检测到登录状态在其他标签页发生变化，正在同步...')
    
    // 强制刷新当前页面，让 Vue Router 和 Pinia 重新读取最新的 Token
    window.location.reload()
  }
}

// 监听 token 变化，自动连接/断开 WebSocket
watch(() => userStore.token, (newToken) => {
  if (newToken) {
    chatStore.connectSocket() // 登录后立即全局连线
  } else {
    chatStore.disconnectSocket() // 登出后断开
  }
}, { immediate: true }) // 确保页面刚刷新时如果已登录也自动连线

onMounted(() => {
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange)
})
</script>