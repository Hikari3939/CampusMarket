import request from './request'

// 获取商品列表 (支持模糊搜索)
export const getProducts = (keyword = '') => request.get('/products', { params: { keyword } });

// 获取单条商品详情
export const getProductDetail = (id) => request.get(`/products/${id}`);

// 删除商品
export const deleteProduct = (id) => request.delete(`/products/${id}`);

// 发布商品 (使用 FormData 包含图片)
export const createProduct = (formData) => {
  return request.post('/products', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

