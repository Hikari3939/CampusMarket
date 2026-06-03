import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '');
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'));

  const setToken = (newToken) => {
    token.value = newToken;
    localStorage.setItem('token', newToken);
  };

  const setUserInfo = (info) => {
    // 合并而非替换，保留未传入的字段（如 avatar_url）
    userInfo.value = { ...userInfo.value, ...info };
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value));
  };

  const updateAvatarUrl = (url) => {
    userInfo.value.avatar_url = url;
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value));
  };

  const logout = () => {
    token.value = '';
    userInfo.value = {};
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
  };

  return { token, userInfo, setToken, setUserInfo, updateAvatarUrl, logout };
});