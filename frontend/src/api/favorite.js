import request from './request'

export const toggleFavorite = (productId) => {
  return request.post('/favorites', { product_id: productId })
}

export const getFavorites = (params = {}) => request.get('/favorites', { params })

export const checkFavorites = (ids) => {
  return request.get('/favorites/check', { params: { ids: ids.join(',') } })
}
