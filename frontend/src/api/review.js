import request from './request'

export const createReview = (data) => request.post('/reviews', data)

export const checkReviewed = (orderId) => request.get(`/reviews/check/${orderId}`)

export const getUserReviews = (userId) => request.get(`/users/${userId}/reviews`)
