import request from './request';

export const loginAPI = (data) => request.post('/auth/login', data);
export const registerAPI = (data) => request.post('/auth/register', data);