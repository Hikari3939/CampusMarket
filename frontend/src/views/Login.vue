<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-banner">
        <h2>东南大学二手交易平台</h2>
        <p>安全·便捷·校园专属</p>
        <div class="vis-color-blocks">
          <div class="color-block green"></div>
          <div class="color-block yellow"></div>
          <div class="color-block orange"></div>
        </div>
      </div>

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
            <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
              <el-form-item prop="username">
                <el-input v-model="registerForm.username" placeholder="设置用户名 (2-50个字符)" size="large" maxlength="50" show-word-limit />
              </el-form-item>
              <el-form-item prop="email">
                <el-input v-model="registerForm.email" placeholder="邮箱 (推荐使用@seu.edu.cn)" size="large" />
              </el-form-item>
              <el-form-item prop="password">
                <el-input v-model="registerForm.password" type="password" placeholder="至少6位，需包含字母和数字" size="large" show-password />
                <div class="password-hint">密码需至少6位，且同时包含字母和数字</div>
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
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/user';
import { loginAPI, registerAPI } from '../api/auth';
import { ElMessage } from 'element-plus';

const router = useRouter();
const userStore = useUserStore();

const activeTab = ref('login');
const loading = ref(false);
const registerFormRef = ref(null);

const loginForm = ref({ email: '', password: '' });
const registerForm = reactive({ username: '', email: '', password: '' });

const validatePassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'));
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'));
  } else if (!/[A-Za-z]/.test(value)) {
    callback(new Error('密码必须包含至少一个字母'));
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含至少一个数字'));
  } else {
    callback();
  }
};

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度应在2-50个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'blur' }
  ]
};

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
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!registerFormRef.value) return;
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return;
    loading.value = true;
    try {
      await registerAPI(registerForm);
      ElMessage.success('注册成功，请登录');
      activeTab.value = 'login';
      loginForm.value.email = registerForm.email;
    } finally {
      loading.value = false;
    }
  });
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
  box-shadow: 0 10px 30px rgba(35, 24, 21, 0.08);
  overflow: hidden;
}

.login-banner {
  flex: 1;
  background-color: var(--seu-dark-blue);
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
  border-radius: 6px;
}

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

.password-hint {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 4px;
  line-height: 1.4;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e4e7ed;
}
:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: bold;
}
</style>
