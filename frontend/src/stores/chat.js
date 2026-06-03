// src/stores/chat.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { io } from 'socket.io-client'
import { useUserStore } from './user'
import { getContacts, getChatHistory } from '../api/message'
import { ElMessage } from 'element-plus'

export const useChatStore = defineStore('chat', () => {
  const socket = ref(null)
  const isConnected = ref(false)
  const contacts = ref([])
  const currentContact = ref(null)
  const currentMessages = ref([])

  const userStore = useUserStore()

  // 初始化 WebSocket 连接
  const connectSocket = () => {
    if (!userStore.token) return
    if (socket.value && socket.value.connected) return

    // WebSocket 地址 — 优先使用环境变量
    const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL
      || import.meta.env.VITE_API_BASE_URL
      || `http://${window.location.hostname}:5000`
    socket.value = io(WS_BASE_URL, {
      auth: { token: userStore.token },
      transports: ['websocket', 'polling']
    })

    socket.value.on('connect', () => {
      isConnected.value = true
    })

    socket.value.on('disconnect', () => {
      isConnected.value = false
    })

    // 在 connectSocket 方法中补充监听：
    socket.value.on('message_sent', (realMsg) => {
      // 找到使用假 ID 的消息，替换为数据库真实返回的消息
      const index = currentMessages.value.findIndex(
        m => m.content === realMsg.content && m.sender_id === realMsg.sender_id
      )
      if (index !== -1) {
        currentMessages.value[index] = realMsg
      }
    })

    // 接收到新消息时的处理逻辑
    socket.value.on('receive_message', (msg) => {
      // 1. 如果正好在和发信人聊天，直接 push 到当前窗口
      if (currentContact.value && Number(currentContact.value.id) === Number(msg.sender_id)) {
        currentMessages.value.push(msg)
        socket.value.emit('mark_as_read', { message_id: msg.id })
      } else {
        // 2. 否则，全局提示，并在联系人列表中增加未读数
        ElMessage.info('您有一条新私信')
        loadContacts() // 重新拉取联系人列表以刷新未读数并将其置顶
      }
    })

    // 监听报错
    socket.value.on('error', (err) => {
      ElMessage.error(err.msg || '实时通讯异常')
    })
  }

  // 主动断开连接 (退出登录时调用)
  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
      currentContact.value = null
      currentMessages.value = []
    }
  }

  // 加载联系人列表
  const loadContacts = async () => {
    try {
      const res = await getContacts()
      contacts.value = res.data
    } catch (error) {}
  }

  // 加载特定联系人的历史记录
  const loadHistory = async (contactId) => {
    try {
      const res = await getChatHistory(contactId)
      currentContact.value = res.data.contact
      currentMessages.value = res.data.messages
      
      // 清除该联系人在列表中的未读红点
      const contactInList = contacts.value.find(c => c.id === Number(contactId))
      if (contactInList) contactInList.unread_count = 0
    } catch (error) {}
  }

  // 发送消息
  const sendMessage = (receiverId, content) => {
    if (!socket.value || !isConnected.value) {
      ElMessage.warning('连接已断开，请刷新重试')
      return
    }

    const msgPayload = { receiver_id: receiverId, content }
    // 本地乐观更新，先将消息显示在屏幕上
    const tempMsg = {
      id: Date.now(),
      sender_id: userStore.userInfo.id,
      receiver_id: receiverId,
      content: content,
      created_at: new Date().toLocaleString()
    }
    currentMessages.value.push(tempMsg)
    
    // 发送给后端
    socket.value.emit('send_message', msgPayload)
    loadContacts() // 发送后更新联系人列表最新消息
  }

  return {
    socket,
    isConnected,
    contacts,
    currentContact,
    currentMessages,
    connectSocket,
    disconnectSocket,
    loadContacts,
    loadHistory,
    sendMessage
  }
})