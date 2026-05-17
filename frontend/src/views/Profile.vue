<!-- src/views/Profile.vue -->
<template>
  <div class="page-container">
    <!-- 用户信息头部 (简易版) -->
    <div class="profile-header">
      <el-avatar :size="64" class="user-avatar">{{ userStore.userInfo?.username?.charAt(0) }}</el-avatar>
      <div class="user-info">
        <h2>{{ userStore.userInfo?.username }}</h2>
        <p>{{ userStore.userInfo?.email }}</p>
      </div>
    </div>

    <!-- 历史记录分栏 -->
    <el-card class="history-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        
        <!-- Tab 1: 我发布的 -->
        <el-tab-pane label="我发布的" name="published">
          <div v-loading="loadingPublished" class="list-container">
            <el-empty v-if="publishedList.length === 0" description="暂无发布记录" />
            
            <div v-for="item in publishedList" :key="item.id" class="list-item">
              <el-image :src="item.image_url" fit="cover" class="item-img"></el-image>
              <div class="item-main">
                <div class="item-title">{{ item.title }}</div>
                <div class="item-time">发布时间：{{ item.created_at }}</div>
              </div>
              <div class="item-side">
                <div class="item-price">¥ {{ item.price }}</div>
                <!-- 状态标签应用 VIS 辅助色彩 -->
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

        <!-- Tab 2: 我买到的 -->
        <el-tab-pane label="我买到的" name="bought">
          <div v-loading="loadingBought" class="list-container">
            <el-empty v-if="boughtList.length === 0" description="暂无购买记录" />
            
            <div v-for="order in boughtList" :key="order.order_id" class="list-item">
              <el-image :src="order.product.image_url" fit="cover" class="item-img"></el-image>
              <div class="item-main">
                <div class="item-title">{{ order.product.title }}</div>
                <div class="item-desc">订单号：{{ order.order_no }}</div>
                <div class="item-time">交易时间：{{ order.order_time }} | 卖家：{{ order.product.seller_name }}</div>
              </div>
              <div class="item-side">
                <div class="item-price">¥ {{ order.deal_price }}</div>
                <el-tag color="var(--seu-orange)" effect="dark" class="custom-tag">
                  交易成功
                </el-tag>
              </div>
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { getMyPublished, getMyBought } from '../api/user'

const userStore = useUserStore()
const route = useRoute()

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

// 获取发布历史
const fetchPublished = async () => {
  if (publishedList.value.length > 0) return // 简易缓存避免重复请求
  loadingPublished.value = true
  try {
    const res = await getMyPublished()
    publishedList.value = res.data
  } finally {
    loadingPublished.value = false
  }
}

// 获取购买历史
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

// Tab 切换处理按需加载
const handleTabChange = (tabName) => {
  if (tabName === 'published') fetchPublished()
  if (tabName === 'bought') fetchBought()
}

onMounted(() => {
  // 检查 URL 参数是否要求直接打开某个 Tab（例如支付成功跳转过来）
  if (route.query.tab === 'bought') {
    activeTab.value = 'bought'
    fetchBought()
  } else {
    fetchPublished()
  }
})
</script>

<style scoped>
/* 个人中心头部 */
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
}
.user-info h2 {
  color: var(--seu-black);
  margin-bottom: 6px;
}
.user-info p {
  color: var(--text-light);
  font-size: 14px;
}

/* 覆盖 Tabs 的指示器为东南绿 */
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

/* 列表容器重置 */
.history-card {
  min-height: 500px;
  padding: 10px 20px;
}

/* 列表单项：现代扁平化布局 */
.list-item {
  display: flex;
  align-items: center;
  padding: 20px 0;
  border-bottom: 1px solid #f0f2f5;
  transition: background-color 0.3s;
}
.list-item:hover {
  background-color: #fafafa;
}
.list-item:last-child {
  border-bottom: none;
}

/* 左侧图片 */
.item-img {
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius-base);
  margin-right: 20px;
  background-color: #f5f7fa;
}

/* 中间主信息 */
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

/* 右侧价格与状态 */
.item-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  height: 70px;
  min-width: 100px;
}
.item-price {
  font-size: 18px;
  font-weight: bold;
  color: var(--seu-orange); /* 使用东南活泼橙展示金额 */
}
.custom-tag {
  border: none;
  border-radius: 4px;
}
</style>