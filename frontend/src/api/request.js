import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../stores/user';
import router from '../router';

const currentHost = window.location.hostname
const request = axios.create({
  baseURL: `http://${currentHost}:5000/api`, // 指向你的 Flask 后端
  timeout: 5000
});

// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// 响应拦截器
request.interceptors.response.use(response => {
  return response.data;
}, error => {
  // 获取 HTTP 状态码
  const status = error.response ? error.response.status : null;
  // 如果是 401 (未授权/Token过期)
  if (status === 401) {
    const userStore = useUserStore();
    ElMessage.error('登录状态已过期，请重新登录'); 
    // 清除 Pinia 和 LocalStorage 中的 Token
    userStore.logout();
    // 跳转到登录页
    router.push({path: '/login'});
  }
  else {
    const msg = error.response?.data?.msg || '网络请求错误';
    ElMessage.error(msg);
    return Promise.reject(error);
  }
});

export default request;