import request from './request'

// 获取商品列表 (支持模糊搜索、分类筛选、分页)
export const getProducts = (params = {}) => request.get('/products', { params });
// params: { keyword?, category?, page?, per_page? }

// 获取单条商品详情
export const getProductDetail = (id) => request.get(`/products/${id}`);

// 删除商品
export const deleteProduct = (id) => request.delete(`/products/${id}`);

// 发布商品 (使用 FormData 包含图片)
export const createProduct = (formData, config = {}) => {
  return request.post('/products', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...config
  })
}

// 编辑商品
export const updateProduct = (id, formData, config = {}) => {
  return request.put(`/products/${id}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    ...config
  })
}
