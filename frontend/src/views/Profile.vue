<!-- src/views/Profile.vue -->
<template>
  <div class="page-container">
    <div class="profile-header">
      <el-avatar :size="64" class="user-avatar">{{ userStore.userInfo?.username?.charAt(0) }}</el-avatar>
      <div class="user-info">
        <h2>{{ userStore.userInfo?.username }}</h2>
        <p>{{ userStore.userInfo?.email }}</p>
      </div>
      <div class="profile-actions">
        <el-button text :icon="Edit" @click="showProfileDialog = true">编辑资料</el-button>
      </div>
    </div>

    <el-card class="history-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">

        <el-tab-pane label="我发布的" name="published">
          <div v-loading="loadingPublished" class="list-container">
            <el-empty v-if="publishedList.length === 0" description="暂无发布记录" />

            <div v-for="item in publishedList" :key="item.id" class="list-item" @click="router.push(`/product/${item.id}`)">
              <el-image :src="item.image_url" fit="cover" class="item-img"></el-image>
              <div class="item-main">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-time">发布时间：{{ item.created_at }}</div>
              </div>
              <div class="item-side">
                <div class="item-price">¥ {{ item.price }}</div>
                <el-tag
                  :type="item.status === 'active' ? 'success' : (item.status === 'sold' ? 'warning' : 'info')"
                  :color="item.status === 'active' ? 'var(--seu-green)' : (item.status === 'sold' ? 'var(--seu-orange)' : '#ccc')"
                  effect="dark"
                  class="custom-tag">
                  {{ statusMap[item.status] }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我买到的" name="bought">
          <div v-loading="loadingBought" class="list-container">
            <el-empty v-if="boughtList.length === 0" description="暂无购买记录" />

            <div v-for="order in boughtList" :key="order.order_id" class="list-item">
              <el-image :src="order.product.image_url" fit="cover" class="item-img" @click.stop="router.push(`/product/${order.product.id}`)"></el-image>
              <div class="item-main">
                <div class="item-title">{{ order.product.title }}</div>
                <div class="item-desc">订单号：{{ order.order_no }}</div>
                <div class="item-time">交易时间：{{ order.order_time }} | 卖家：{{ order.product.seller_name }}</div>
              </div>
              <div class="item-side">
                <div class="item-price">¥ {{ order.deal_price }}</div>
                <div>
                  <el-tag
                    :color="order.order_status === 'completed' ? 'var(--seu-orange)' : '#ccc'"
                    effect="dark"
                    class="custom-tag">
                    {{ order.order_status === 'completed' ? '交易成功' : '已取消' }}
                  </el-tag>
                  <el-button
                    v-if="order.order_status === 'completed'"
                    type="danger"
                    text
                    size="small"
                    style="margin-top: 8px;"
                    @click.stop="handleCancelOrder(order)">
                    取消订单
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>

    <!-- 编辑资料对话框 -->
    <el-dialog v-model="showProfileDialog" title="编辑个人资料" width="480px" :close-on-click-modal="false">
      <el-tabs>
        <el-tab-pane label="修改用户名">
          <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" maxlength="50" show-word-limit />
            </el-form-item>
          </el-form>
          <el-button type="primary" :loading="savingProfile" @click="submitProfile" style="width: 100%;">保存</el-button>
        </el-tab-pane>

        <el-tab-pane label="修改密码">
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef">
            <el-form-item label="旧密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" show-password />
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password" show-password />
            </el-form-item>
          </el-form>
          <el-button type="primary" :loading="savingPassword" @click="submitPassword" style="width: 100%;">修改密码</el-button>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getMyPublished, getMyBought, updateProfile, updatePassword } from '../api/user'
import { cancelOrder } from '../api/order'
import { Edit } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('published')
const publishedList = ref([])
const boughtList = ref([])
const loadingPublished = ref(false)
const loadingBought = ref(false)

const statusMap = {
  'active': '在售中',
  'sold': '已售出',
  'deleted': '已下架'
}

// --- Edit profile dialog ---
const showProfileDialog = ref(false)
const profileFormRef = ref(null)
const passwordFormRef = ref(null)
const savingProfile = ref(false)
const savingPassword = ref(false)

const profileForm = reactive({ username: '' })
const profileRules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度应在2-50个字符之间', trigger: 'blur' }
  ]
}

const passwordForm = reactive({ old_password: '', new_password: '', confirm_password: '' })
const validateConfirmPassword = (_rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}
const validateNewPassword = (_rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能少于6位'))
  } else if (!/[A-Za-z]/.test(value)) {
    callback(new Error('密码必须包含至少一个字母'))
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含至少一个数字'))
  } else {
    callback()
  }
}
const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [{ required: true, validator: validateNewPassword, trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// Watch dialog open to pre-fill
const openProfileDialog = () => { showProfileDialog.value = true } // triggered by button

const submitProfile = async () => {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return
    savingProfile.value = true
    try {
      const res = await updateProfile({ username: profileForm.username })
      userStore.setUserInfo({ ...userStore.userInfo, username: res.data.username })
      ElMessage.success('资料更新成功')
      showProfileDialog.value = false
    } catch (e) {} finally {
      savingProfile.value = false
    }
  })
}

const submitPassword = async () => {
  if (!passwordFormRef.value) return
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    savingPassword.value = true
    try {
      await updatePassword({
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      ElMessage.success('密码修改成功，请重新登录')
      userStore.logout()
      router.push('/login')
    } catch (e) {} finally {
      savingPassword.value = false
    }
  })
}

// --- Order cancel ---
const handleCancelOrder = (order) => {
  ElMessageBox.confirm('取消订单后商品将重新上架，确定要取消吗？', '确认取消', {
    confirmButtonText: '确定', cancelButtonText: '再想想', type: 'warning',
  }).then(async () => {
    try {
      await cancelOrder(order.order_id)
      ElMessage.success('订单已取消')
      boughtList.value = []
      fetchBought()
    } catch (e) {}
  }).catch(() => {})
}

// --- Data fetching ---
const fetchPublished = async () => {
  if (publishedList.value.length > 0) return
  loadingPublished.value = true
  try {
    const res = await getMyPublished()
    publishedList.value = res.data
  } finally {
    loadingPublished.value = false
  }
}

const fetchBought = async () => {
  if (boughtList.value.length > 0) return
  loadingBought.value = true
  try {
    const res = await getMyBought()
    boughtList.value = res.data
  } finally {
    loadingBought.value = false
  }
}

const handleTabChange = (tabName) => {
  if (tabName === 'published') fetchPublished()
  if (tabName === 'bought') fetchBought()
}

onMounted(() => {
  // Pre-fill profile form
  profileForm.username = userStore.userInfo?.username || ''
  if (route.query.tab === 'bought') {
    activeTab.value = 'bought'
    fetchBought()
  } else {
    fetchPublished()
  }
})
</script>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 0;
}
.user-avatar {
  background-color: var(--seu-green);
  font-size: 24px;
  font-weight: bold;
}
.user-info {
  margin-left: 20px;
  flex: 1;
}
.user-info h2 {
  color: var(--seu-black);
  margin-bottom: 6px;
}
.user-info p {
  color: var(--text-light);
  font-size: 14px;
}
.profile-actions {
  margin-left: auto;
}

:deep(.el-tabs__active-bar) {
  background-color: var(--seu-green);
}
:deep(.el-tabs__item.is-active),
:deep(.el-tabs__item:hover) {
  color: var(--seu-green);
}
:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

.history-card {
  min-height: 500px;
  padding: 10px 20px;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.3s;
  cursor: pointer;
}
.list-item:hover {
  background-color: #fafafa;
}
.list-item:last-child {
  border-bottom: none;
}

.item-img {
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius-base);
  margin-right: 20px;
  background-color: #f5f7fa;
}

.item-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 70px;
}
.item-title {
  font-size: 16px;
  color: var(--seu-black);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.item-desc {
  font-size: 13px;
  color: var(--text-light);
}
.item-time {
  font-size: 13px;
  color: var(--text-light);
}

.item-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  height: 70px;
  min-width: 120px;
}
.item-price {
  font-size: 18px;
  font-weight: bold;
  color: var(--seu-orange);
}
.custom-tag {
  border: none;
  border-radius: 4px;
}
</style>
