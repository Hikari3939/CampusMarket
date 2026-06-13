import request from './request'

export const getProducts = (params = {}) => request.get('/products', { params });

export const getProductDetail = (id) => request.get(`/products/${id}`);

export const deleteProduct = (id) => request.delete(`/products/${id}`);

export const createProduct = (formData, config = {}) => {
  return request.post('/products', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    ...config
  })
}

export const updateProduct = (id, formData, config = {}) => {
  return request.put(`/products/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    ...config
  })
}
