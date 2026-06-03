import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useUserStore } from '../stores/user';
import router from '../router';

// 优先使用环境变量，fallback 到当前主机名
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
  || `http://${window.location.hostname}:5000`;

const request = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000
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

  // 网络超时或服务器不可达
  if (!status) {
    ElMessage.error('网络连接失败，请检查网络设置');
    return Promise.reject(error);
  }

  // 如果是 401 (未授权/Token过期)
  if (status === 401) {
    const userStore = useUserStore();
    ElMessage.error('登录状态已过期，请重新登录');
    // 清除 Pinia 和 LocalStorage 中的 Token
    userStore.logout();
    // 跳转到登录页
    router.push({ path: '/login' });
    return Promise.reject(error);
  }

  // 其他错误（由后端返回的 msg 统一弹窗）
  const msg = error.response?.data?.msg || '网络请求错误';
  ElMessage.error(msg);
  return Promise.reject(error);
});

export default request;
