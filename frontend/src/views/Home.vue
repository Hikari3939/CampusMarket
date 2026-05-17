<!-- src/views/Home.vue -->
<template>
  <div class="home-layout">
    <!-- 全局顶部导航栏 -->
    <header class="app-header">
      <div class="header-content">
        <!-- 左侧 Logo / 标题 -->
        <div class="brand">
          <span class="brand-text">SEU 闲置流转</span>
        </div>

        <!-- 中部核心搜索区 -->
        <div class="search-center">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索 SEU 二手好物 (如: 高数教材)..."
            class="large-search-input"
            size="large"
            clearable
            @keyup.enter="fetchProducts"
            @clear="fetchProducts"
          >
            <template #append>
              <el-button :icon="Search" @click="fetchProducts" class="search-btn" />
            </template>
          </el-input>
        </div>

        <!-- 右侧操作区 -->
        <div class="user-actions">
          <el-button type="primary" :icon="Plus" @click="goToPublish" round>
            发布闲置
          </el-button>
          
          <!-- 用户下拉菜单 (已登录状态) -->
          <el-dropdown @command="handleCommand" v-if="userStore.token">
            <span class="user-dropdown-link">
              {{ userStore.userInfo?.username || '我的' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <!-- 消息中心 -->
                <el-dropdown-item command="chat">
                  消息中心
                </el-dropdown-item>
                <!-- 个人中心 -->
                <el-dropdown-item command="profile">
                  个人中心
                </el-dropdown-item>
                <!-- 退出登录 -->
                <el-dropdown-item command="logout" divided style="color: #F56C6C;">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          
          <!-- 未登录状态 -->
          <el-button v-else text @click="router.push('/login')">登录 / 注册</el-button>
        </div>
      </div>
    </header>

    <!-- 瀑布流商品列表区 -->
    <main class="page-container main-content">
      <div class="product-grid" v-loading="loading">
        <template v-if="products.length > 0">
          <ProductCard 
            v-for="item in products" 
            :key="item.id" 
            :product="item"
            @delete="handleDeleteClick"
            @click="goToDetail(item.id)"
          />
        </template>
        <el-empty v-else description="暂无相关商品，快去抢首发吧！" class="empty-state" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, ArrowDown } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProductCard from '../components/ProductCard.vue'
import { getProducts, deleteProduct } from '../api/product'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore() // 引入全局状态
const products = ref([])
const searchKeyword = ref('')
const loading = ref(false)

// 拉取商品
const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await getProducts(searchKeyword.value)
    products.value = res.data
  } catch (error) {
    // 拦截器已处理
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchProducts())

const goToPublish = () => router.push('/publish')
const goToDetail = (id) => router.push(`/product/${id}`)

// 处理右上角下拉菜单指令
const handleCommand = (command) => {
  if (command === 'profile') {
    // 跳转到个人中心页
    router.push('/profile')
  } else if (command === 'chat') {
    // 跳转到消息中心页
    router.push('/chat')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      userStore.logout() // 调用登出方法
      ElMessage.success('已安全退出')
      // 登出后刷新列表
      fetchProducts()
    }).catch(() => {})
  }
}

// 处理删除逻辑
const handleDeleteClick = (id) => {
  ElMessageBox.confirm('确定要下架并删除该商品吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProduct(id)
      ElMessage.success('删除成功')
      fetchProducts()
    } catch (error) {}
  }).catch(() => {})
}
</script>

<style scoped>
.home-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部导航栏样式 */
.app-header {
  background-color: #ffffff;
  box-shadow: var(--box-shadow-base);
  position: sticky; /* 吸顶效果 */
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

/* 左侧品牌区 */
.brand {
  flex: 1;
  display: flex;
  align-items: center;
}
.brand-text {
  font-size: 22px;
  font-weight: 600;
  color: var(--seu-green);
  letter-spacing: 1px;
}

/* 中部搜索区 */
.search-center {
  flex: 2;
  display: flex;
  justify-content: center;
}
.large-search-input {
  width: 100%;
  max-width: 560px; /* 限制最大宽度，保证屏幕足够大时不会无限拉长 */
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); /* 搜索框自带轻微悬浮感 */
  border-radius: 4px;
}

/* 右侧操作区 */
.user-actions {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}
.user-dropdown-link {
  cursor: pointer;
  color: var(--seu-black);
  display: flex;
  align-items: center;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}
.user-dropdown-link:hover {
  background-color: #f4f6f8;
}

/* 主内容区 */
.main-content {
  flex: 1;
  /* 定义准确的宽度和居中对齐边界，与顶部导航保持统一视野 */
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px 64px; 
  box-sizing: border-box;
}

.product-grid {
  display: grid;
  /* 使得商品自适应宽度占满整行剩余空间 */
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
  /* 网格容器强制占满主内容区 */
  width: 100%; 
  min-height: 400px;
}

.empty-state {
  grid-column: 1 / -1;
}
</style>