import request from './request'

// 获取我发布的历史
export const getMyPublished = () => {
  return request({
    url: '/users/me/published',
    method: 'GET'
  })
}

// 获取我购买的历史
export const getMyBought = () => {
  return request({
    url: '/users/me/bought',
    method: 'GET'
  })
}