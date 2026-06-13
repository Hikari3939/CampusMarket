import request from './request'

export const getMyPublished = () => request.get('/users/me/published')

export const getMyBought = () => request.get('/users/me/bought')

export const updateProfile = (data) => {
  const isFormData = data instanceof FormData
  return request.put('/users/me', data, {
    headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {}
  })
}

export const updatePassword = (data) => request.put('/users/me/password', data)

export const getUserProfile = (id) => request.get(`/users/${id}/profile`)
