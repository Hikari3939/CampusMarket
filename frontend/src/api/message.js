import request from './request'

export function getContacts() {
  return request.get('/messages/contacts')
}

export function getChatHistory(contactId) {
  return request.get(`/messages/history/${contactId}`)
}
