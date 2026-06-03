import request from './request'

// 收藏/取消收藏（切换）
export const toggleFavorite = (productId) => {
  return request.post('/favorites', { product_id: productId })
}

// 获取收藏列表
export const getFavorites = (params = {}) => {
  return request.get('/favorites', { params })
}

// 批量检查收藏状态
export const checkFavorites = (ids) => {
  return request.get('/favorites/check', { params: { ids: ids.join(',') } })
}
