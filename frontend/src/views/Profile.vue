<!-- src/views/Profile.vue -->
<template>
  <div class="page-container">
    <div class="profile-header">
      <el-avatar :size="64" class="user-avatar">
        <img v-if="userStore.userInfo?.avatar_url" :src="userStore.userInfo.avatar_url" style="width:100%;height:100%;object-fit:cover" />
        <span v-else>{{ userStore.userInfo?.username?.charAt(0) }}</span>
      </el-avatar>
      <div class="user-info">
        <h2>{{ userStore.userInfo?.username }}</h2>
        <p>{{ userStore.userInfo?.email }}</p>
      </div>
      <div class="profile-actions">
        <el-button text :icon="Edit" @click="openEditDialog">编辑资料</el-button>
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

        <el-tab-pane label="我的收藏" name="favorites">
          <div v-loading="loadingFavorites" class="list-container">
            <el-empty v-if="favoritesList.length === 0" description="暂无收藏的商品" />

            <div class="product-grid" v-else>
              <ProductCard
                v-for="item in favoritesList"
                :key="item.id"
                :product="item"
                @click="router.push(`/product/${item.id}`)"
              />
            </div>

            <!-- 分页 -->
            <div v-if="favoritesTotal > favoritesList.length" class="load-more-area">
              <el-button :loading="loadingMoreFavorites" @click="loadMoreFavorites">加载更多</el-button>
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
                    v-if="order.order_status === 'completed' && !order.reviewed"
                    type="warning"
                    text
                    size="small"
                    style="margin-top: 8px;"
                    @click.stop="openReviewDialog(order)">
                    评价
                  </el-button>
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
            <el-form-item label="头像">
              <div class="avatar-upload-row">
                <el-avatar :size="64" class="avatar-preview">
                  <img v-if="avatarPreviewUrl || userStore.userInfo?.avatar_url" :src="avatarPreviewUrl || userStore.userInfo.avatar_url" style="width:100%;height:100%;object-fit:cover" />
                  <span v-else>{{ userStore.userInfo?.username?.charAt(0) }}</span>
                </el-avatar>
                <el-upload
                  class="avatar-uploader"
                  action="#"
                  :auto-upload="false"
                  :show-file-list="false"
                  :on-change="handleAvatarChange"
                  accept="image/png, image/jpeg, image/jpg, image/gif"
                >
                  <el-button size="small" type="primary" plain>更换头像</el-button>
                </el-upload>
              </div>
              <div class="upload-tip">支持 png/jpg/jpeg/gif 格式</div>
            </el-form-item>
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

    <!-- 评价对话框 -->
    <el-dialog v-model="showReviewDialog" title="评价交易" width="420px" :close-on-click-modal="false">
      <el-form :model="reviewForm" ref="reviewFormRef" label-position="top">
        <el-form-item label="评分" required>
          <StarRating v-model="reviewForm.rating" />
        </el-form-item>
        <el-form-item label="评价内容">
          <el-input v-model="reviewForm.comment" type="textarea" :rows="3" maxlength="200" show-word-limit placeholder="说说这次交易的体验吧..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" :loading="submittingReview" @click="submitReview">提交评价</el-button>
      </template>
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
import { getFavorites } from '../api/favorite'
import { createReview, checkReviewed } from '../api/review'
import ProductCard from '../components/ProductCard.vue'
import StarRating from '../components/StarRating.vue'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const activeTab = ref('published')
const publishedList = ref([])
const boughtList = ref([])
const favoritesList = ref([])
const favoritesPage = ref(1)
const favoritesTotal = ref(0)
const loadingPublished = ref(false)
const loadingBought = ref(false)
const loadingFavorites = ref(false)
const loadingMoreFavorites = ref(false)

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

const avatarSelectedFile = ref(null)
const avatarPreviewUrl = ref('')

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
const openEditDialog = () => {
  profileForm.username = userStore.userInfo?.username || ''
  avatarSelectedFile.value = null
  avatarPreviewUrl.value = ''
  showProfileDialog.value = true
}

const handleAvatarChange = (uploadFile) => {
  const file = uploadFile.raw
  if (file.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  avatarSelectedFile.value = file
  avatarPreviewUrl.value = URL.createObjectURL(file)
}

const submitProfile = async () => {
  if (!profileFormRef.value) return
  await profileFormRef.value.validate(async (valid) => {
    if (!valid) return
    savingProfile.value = true
    try {
      let res
      if (avatarSelectedFile.value) {
        // 有头像文件时使用 FormData
        const formData = new FormData()
        formData.append('username', profileForm.username)
        formData.append('avatar', avatarSelectedFile.value)
        res = await updateProfile(formData)
      } else {
        res = await updateProfile({ username: profileForm.username })
      }
      userStore.setUserInfo({
        username: res.data.username,
        avatar_url: res.data.avatar_url
      })
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

// --- Reviews ---
const showReviewDialog = ref(false)
const reviewFormRef = ref(null)
const submittingReview = ref(false)
const reviewForm = reactive({ rating: 0, comment: '' })
const currentReviewOrder = ref(null)

const openReviewDialog = (order) => {
  currentReviewOrder.value = order
  reviewForm.rating = 0
  reviewForm.comment = ''
  showReviewDialog.value = true
}

const submitReview = async () => {
  if (reviewForm.rating < 1 || reviewForm.rating > 5) {
    ElMessage.warning('请选择评分')
    return
  }
  submittingReview.value = true
  try {
    await createReview({
      order_id: currentReviewOrder.value.order_id,
      rating: reviewForm.rating,
      comment: reviewForm.comment
    })
    ElMessage.success('评价提交成功')
    showReviewDialog.value = false
    // 标记已评价
    currentReviewOrder.value.reviewed = true
  } catch (e) {} finally {
    submittingReview.value = false
  }
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
    // 检查每个订单的评价状态
    for (const order of boughtList.value) {
      if (order.order_status === 'completed') {
        try {
          const checkRes = await checkReviewed(order.order_id)
          order.reviewed = checkRes.data.reviewed
        } catch (e) {
          order.reviewed = false
        }
      }
    }
  } finally {
    loadingBought.value = false
  }
}

// --- Favorites ---
const fetchFavorites = async () => {
  if (favoritesList.value.length > 0) return
  loadingFavorites.value = true
  favoritesPage.value = 1
  try {
    const res = await getFavorites({ page: 1, per_page: 12 })
    favoritesList.value = res.data
    favoritesTotal.value = res.pagination.total
  } finally {
    loadingFavorites.value = false
  }
}

const loadMoreFavorites = async () => {
  loadingMoreFavorites.value = true
  favoritesPage.value++
  try {
    const res = await getFavorites({ page: favoritesPage.value, per_page: 12 })
    favoritesList.value.push(...res.data)
    favoritesTotal.value = res.pagination.total
  } catch (e) {
    favoritesPage.value--
  } finally {
    loadingMoreFavorites.value = false
  }
}

const handleTabChange = (tabName) => {
  if (tabName === 'published') fetchPublished()
  if (tabName === 'bought') fetchBought()
  if (tabName === 'favorites') fetchFavorites()
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

/* 收藏商品网格 */
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}
.load-more-area {
  display: flex;
  justify-content: center;
  padding: 24px 0;
  width: 100%;
}

/* 头像上传 */
.avatar-upload-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.avatar-preview {
  background-color: var(--seu-green);
  font-size: 24px;
  font-weight: bold;
  flex-shrink: 0;
}
.upload-tip {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 8px;
}
</style>
