<template>
  <div class="page-container chat-layout">
    <el-card class="chat-card" :body-style="{ padding: 0, display: 'flex', height: '100%' }">

      <div class="sidebar">
        <div class="sidebar-header">
          <h3>消息中心</h3>
        </div>
        <div class="contacts-list">
          <div
            v-for="contact in contacts"
            :key="contact.id"
            class="contact-item"
            :class="{ active: currentContact?.id === contact.id }"
            @click="selectContact(contact.id)"
          >
            <el-badge :value="contact.unread_count" :hidden="contact.unread_count === 0" class="badge-item">
              <el-avatar :size="40" style="background-color: var(--seu-yellow); color: var(--seu-black)">
                <img v-if="contact.avatar_url" :src="contact.avatar_url" style="width:100%;height:100%;object-fit:cover" />
                <span v-else>{{ contact.username.charAt(0).toUpperCase() }}</span>
              </el-avatar>
            </el-badge>
            <div class="contact-info">
              <div class="contact-name">{{ contact.username }}</div>
              <div class="contact-preview">{{ contact.last_message || '暂无消息' }}</div>
            </div>
            <div class="contact-time" v-if="contact.last_time">
              {{ formatShortTime(contact.last_time) }}
            </div>
          </div>
          <el-empty v-if="contacts.length === 0" description="暂无联系人" :image-size="60" />
        </div>
      </div>

      <div class="main-chat">
        <div v-if="!currentContact" class="empty-chat">
          <el-empty description="选择一个联系人开始聊天吧" />
        </div>

        <div v-else class="chat-window">
          <div class="chat-header">
            <span class="chat-title">与 {{ currentContact.username }} 沟通中</span>
          </div>

          <div class="messages-area" ref="messagesAreaRef">
            <div
              v-for="msg in currentMessages"
              :key="msg.id"
              class="message-wrapper"
              :class="{ 'is-me': msg.sender_id === userInfo.id }"
            >
              <div class="message-bubble">
                {{ msg.content }}
              </div>
              <div class="message-time">{{ formatTime(msg.created_at) }}</div>
            </div>
          </div>

          <div class="input-area">
            <el-input
              v-model="inputMsg"
              type="textarea"
              :rows="3"
              placeholder="输入你想说的话 (Enter 发送)"
              resize="none"
              class="msg-input"
              @keydown.enter.prevent="handleSend"
            />
            <div class="action-bar">
              <el-button type="primary" @click="handleSend" :disabled="!inputMsg.trim()" class="send-btn">
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useChatStore } from '../stores/chat'
import { useUserStore } from '../stores/user'

const route = useRoute()
const chatStore = useChatStore()
const userStore = useUserStore()

const { contacts, currentContact, currentMessages } = storeToRefs(chatStore)
const { userInfo } = storeToRefs(userStore)

const messagesAreaRef = ref(null)
const inputMsg = ref('')

const formatShortTime = (timeStr) => timeStr.split(' ')[1].substring(0, 5)
const formatTime = (timeStr) => timeStr.substring(5, 16)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesAreaRef.value) {
    messagesAreaRef.value.scrollTop = messagesAreaRef.value.scrollHeight
  }
}

const selectContact = async (contactId) => {
  await chatStore.loadHistory(contactId)
  scrollToBottom()
}

const handleSend = () => {
  if (!inputMsg.value.trim() || !currentContact.value) return
  chatStore.sendMessage(currentContact.value.id, inputMsg.value.trim())
  inputMsg.value = ''
  scrollToBottom()
}

watch(currentMessages, () => {
  scrollToBottom()
}, { deep: true })

onMounted(async () => {
  await chatStore.loadContacts()

  const targetUserId = route.query.userId
  if (targetUserId) {
    await selectContact(Number(targetUserId))
    chatStore.loadContacts()
  }
})
</script>

<style scoped>
.chat-layout {
  height: calc(100vh - 100px);
  padding-bottom: 24px;
}
.chat-card {
  height: 100%;
  border-radius: var(--border-radius-base);
  box-shadow: var(--box-shadow-base);
}

.sidebar {
  width: 280px;
  background-color: #fafbfc;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
}
.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #ffffff;
}
.sidebar-header h3 {
  font-size: 16px;
  color: var(--seu-black);
  margin: 0;
}
.contacts-list {
  flex: 1;
  overflow-y: auto;
}
.contact-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f2f4f7;
}
.contact-item:hover {
  background-color: rgba(88, 117, 88, 0.05);
}
.contact-item.active {
  background-color: rgba(88, 117, 88, 0.1);
  border-left: 3px solid var(--seu-green);
}
.contact-info {
  margin-left: 12px;
  flex: 1;
  overflow: hidden;
}
.contact-name {
  font-size: 14px;
  color: var(--seu-black);
  font-weight: 500;
  margin-bottom: 4px;
}
.contact-preview {
  font-size: 12px;
  color: var(--text-light);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.contact-time {
  font-size: 12px;
  color: #c0c4cc;
}

.main-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
}
.empty-chat {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
  font-weight: bold;
  color: var(--seu-black);
}

.messages-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--bg-color);
}
.message-wrapper {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  align-items: flex-start;
}
.message-wrapper.is-me {
  align-items: flex-end;
}
.message-bubble {
  max-width: 60%;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  background-color: #ffffff;
  color: var(--seu-black);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border-top-left-radius: 2px;
}
.is-me .message-bubble {
  background-color: var(--seu-green);
  color: #ffffff;
  border-top-left-radius: 12px;
  border-top-right-radius: 2px;
}
.message-time {
  font-size: 12px;
  color: #b0b4ba;
  margin-top: 6px;
  margin-left: 4px;
}
.is-me .message-time {
  margin-left: 0;
  margin-right: 4px;
}

.input-area {
  padding: 16px 24px;
  background-color: #ffffff;
  border-top: 1px solid #ebeef5;
}
.msg-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}
.msg-input :deep(.el-textarea__inner:focus) {
  background-color: #ffffff;
  box-shadow: 0 0 0 1px var(--seu-green);
}
.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
.send-btn {
  width: 100px;
  border-radius: 6px;
}
</style>
