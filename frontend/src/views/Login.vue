<!-- src/views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <!-- 左侧装饰区 (深邃蓝主题) -->
      <div class="login-banner">
        <h2>东南大学二手交易平台</h2>
        <p>安全·便捷·校园专属</p>
        <div class="vis-color-blocks">
          <div class="color-block green"></div>
          <div class="color-block yellow"></div>
          <div class="color-block orange"></div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="login-form-area">
        <el-tabs v-model="activeTab" class="custom-tabs">
          <el-tab-pane label="学生登录" name="login">
            <el-form :model="loginForm" @keyup.enter="handleLogin">
              <el-form-item>
                <el-input v-model="loginForm.email" placeholder="请输入常用邮箱或统一认证账号" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" show-password />
              </el-form-item>
              <el-button class="submit-btn" type="primary" size="large" @click="handleLogin" :loading="loading">
                登 录
              </el-button>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="新用户注册" name="register">
            <el-form :model="registerForm">
              <el-form-item>
                <el-input v-model="registerForm.username" placeholder="设置用户名 (如: SEU小明)" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.email" placeholder="邮箱 (推荐使用@seu.edu.cn)" size="large" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="registerForm.password" type="password" placeholder="设置密码" size="large" show-password />
              </el-form-item>
              <el-button class="submit-btn register-btn" size="large" @click="handleRegister" :loading="loading">
                注 册
              </el-button>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { loginAPI, registerAPI } from '../api/auth';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();

const activeTab = ref('login');
const loading = ref(false);

const loginForm = ref({ email: '', password: '' });
const registerForm = ref({ username: '', email: '', password: '' });

const handleLogin = async () => {
  if (!loginForm.value.email || !loginForm.value.password) {
    return ElMessage.warning('请填写完整信息');
  }
  loading.value = true;
  try {
    const res = await loginAPI(loginForm.value);
    userStore.setToken(res.token);
    userStore.setUserInfo(res.user);
    ElMessage.success('登录成功！');
    router.push('/');
  } catch (error) {
    // 错误在拦截器中已经处理提示
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    return ElMessage.warning('请填写完整信息');
  }
  loading.value = true;
  try {
    await registerAPI(registerForm.value);
    ElMessage.success('注册成功，请登录');
    activeTab.value = 'login';
    loginForm.value.email = registerForm.value.email;
  } catch (error) {
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: var(--bg-color);
}

.login-box {
  display: flex;
  width: 800px;
  height: 480px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(35, 24, 21, 0.08); /* 使用标准黑的投影 */
  overflow: hidden;
}

.login-banner {
  flex: 1;
  background-color: var(--seu-dark-blue); /* 深邃蓝 */
  color: white;
  padding: 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-banner h2 {
  font-size: 28px;
  margin-bottom: 10px;
  letter-spacing: 2px;
}

.login-banner p {
  color: #a0a6c0;
  font-size: 16px;
  margin-bottom: 40px;
}

/* 品牌色块装饰 */
.vis-color-blocks {
  display: flex;
  gap: 10px;
}
.color-block {
  width: 40px;
  height: 6px;
  border-radius: 3px;
}
.color-block.green { background-color: var(--seu-green); }
.color-block.yellow { background-color: var(--seu-yellow); }
.color-block.orange { background-color: var(--seu-orange); }

.login-form-area {
  flex: 1.2;
  padding: 50px 60px;
  background: #ffffff;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  border-radius: 6px; /* 扁平化圆角 */
}

/* 注册按钮使用辅助色活力橙进行视觉区分 */
.register-btn {
  background-color: var(--seu-orange);
  border-color: var(--seu-orange);
  color: white;
}
.register-btn:hover {
  background-color: #df9b00;
  border-color: #df9b00;
  color: white;
}

/* 修改 Element Plus 的 Tab 样式实现极简风格 */
:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}
:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: bold;
}
</style>