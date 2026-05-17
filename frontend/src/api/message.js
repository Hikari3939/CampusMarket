// src/api/message.js
import request from './request'

// 获取历史联系人列表
export function getContacts() {
  return request({
    url: '/messages/contacts',
    method: 'get'
  })
}

// 获取与某位用户的历史聊天记录
export function getChatHistory(contactId) {
  return request({
    url: `/messages/history/${contactId}`,
    method: 'get'
  })
}