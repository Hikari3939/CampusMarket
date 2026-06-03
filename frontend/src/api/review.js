import request from './request'

// 创建评价
export const createReview = (data) => {
  return request.post('/reviews', data)
}

// 检查是否已评价某订单
export const checkReviewed = (orderId) => {
  return request.get(`/reviews/check/${orderId}`)
}

// 获取用户收到的评价
export const getUserReviews = (userId) => {
  return request.get(`/users/${userId}/reviews`)
}
