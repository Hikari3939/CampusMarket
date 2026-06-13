import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../stores/user';
import router from '../router';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  || `http://${window.location.hostname}:5000`;

const request = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000
});

request.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

request.interceptors.response.use(response => {
  return response.data;
}, error => {
  const status = error.response ? error.response.status : null;

  if (!status) {
    ElMessage.error('网络连接失败，请检查网络设置');
    return Promise.reject(error);
  }

  if (status === 401) {
    const userStore = useUserStore();
    ElMessage.error('登录状态已过期，请重新登录');
    userStore.logout();
    router.push({ path: '/login' });
    return Promise.reject(error);
  }

  const msg = error.response?.data?.msg || '网络请求错误';
  ElMessage.error(msg);
  return Promise.reject(error);
});

export default request;
