import request from './request'

export const createOrder = (data) => {
  return request.post('/orders', data)
}

export const cancelOrder = (id) => {
  return request.put(`/orders/${id}/cancel`)
}
