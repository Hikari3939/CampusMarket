import request from './request'

// 创建订单 (立即购买)
export const createOrder = (data) => {
  return request({
    url: '/orders',
    method: 'POST',
    data // { product_id: xxx }
  })
}