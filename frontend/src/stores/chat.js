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

  const connectSocket = () => {
    if (!userStore.token) return
    if (socket.value && socket.value.connected) return

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

    socket.value.on('message_sent', (realMsg) => {
      const index = currentMessages.value.findIndex(
        m => m.content === realMsg.content && m.sender_id === realMsg.sender_id
      )
      if (index !== -1) {
        currentMessages.value[index] = realMsg
      }
    })

    socket.value.on('receive_message', (msg) => {
      if (currentContact.value && Number(currentContact.value.id) === Number(msg.sender_id)) {
        currentMessages.value.push(msg)
        socket.value.emit('mark_as_read', { message_id: msg.id })
      } else {
        ElMessage.info('您有一条新私信')
        loadContacts()
      }
    })

    socket.value.on('error', (err) => {
      ElMessage.error(err.msg || '实时通讯异常')
    })
  }

  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
      isConnected.value = false
      currentContact.value = null
      currentMessages.value = []
    }
  }

  const loadContacts = async () => {
    try {
      const res = await getContacts()
      contacts.value = res.data
    } catch (error) {}
  }

  const loadHistory = async (contactId) => {
    try {
      const res = await getChatHistory(contactId)
      currentContact.value = res.data.contact
      currentMessages.value = res.data.messages

      const contactInList = contacts.value.find(c => c.id === Number(contactId))
      if (contactInList) contactInList.unread_count = 0
    } catch (error) {}
  }

  const sendMessage = (receiverId, content) => {
    if (!socket.value || !isConnected.value) {
      ElMessage.warning('连接已断开，请刷新重试')
      return
    }

    const tempMsg = {
      id: Date.now(),
      sender_id: userStore.userInfo.id,
      receiver_id: receiverId,
      content: content,
      created_at: new Date().toLocaleString()
    }
    currentMessages.value.push(tempMsg)

    socket.value.emit('send_message', { receiver_id: receiverId, content })
    loadContacts()
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
