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

// 修改个人资料（用户名）
export const updateProfile = (data) => {
  return request({
    url: '/users/me',
    method: 'PUT',
    data
  })
}

// 修改密码
export const updatePassword = (data) => {
  return request({
    url: '/users/me/password',
    method: 'PUT',
    data
  })
}

// 获取用户公开主页
export const getUserProfile = (id) => {
  return request({
    url: `/users/${id}/profile`,
    method: 'GET'
  })
}
