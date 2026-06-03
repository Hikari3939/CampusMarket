<!-- src/views/Home.vue -->
<template>
  <div class="home-layout">
    <header class="app-header">
      <div class="header-content">
        <div class="brand">
          <span class="brand-text">SEU 闲置流转</span>
        </div>

        <div class="search-center">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索 SEU 二手好物 (如: 高数教材)..."
            class="large-search-input"
            size="large"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" class="search-btn" />
            </template>
          </el-input>
        </div>

        <div class="user-actions">
          <el-button type="primary" :icon="Plus" @click="goToPublish" round>
            发布闲置
          </el-button>

          <el-dropdown @command="handleCommand" v-if="userStore.token">
            <span class="user-dropdown-link">
              {{ userStore.userInfo?.username || '我的' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="chat">消息中心</el-dropdown-item>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided style="color: #F56C6C;">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-button v-else text @click="router.push('/login')">登录 / 注册</el-button>
        </div>
      </div>
    </header>

    <main class="page-container main-content">
      <!-- 分类筛选标签 -->
      <div class="category-filter">
        <el-tag
          v-for="cat in categories"
          :key="cat.value"
          :effect="activeCategory === cat.value ? 'dark' : 'plain'"
          :color="activeCategory === cat.value ? 'var(--seu-green)' : ''"
          @click="selectCategory(cat.value)"
          class="category-tag"
        >
          {{ cat.label }}
        </el-tag>
      </div>

      <!-- 商品网格 -->
      <div class="product-grid">
        <!-- 骨架屏（首次加载） -->
        <template v-if="initialLoading">
          <div v-for="n in 8" :key="'s'+n" class="skeleton-card">
            <el-skeleton animated>
              <template #template>
                <el-skeleton-item variant="image" style="width: 100%; height: 200px;" />
                <div style="padding: 14px;">
                  <el-skeleton-item variant="text" style="width: 80%;" />
                  <el-skeleton-item variant="text" style="width: 40%; margin-top: 8px;" />
                </div>
              </template>
            </el-skeleton>
          </div>
        </template>

        <!-- 商品卡片 -->
        <template v-else>
          <ProductCard
            v-for="item in products"
            :key="item.id"
            :product="item"
            @delete="handleDeleteClick"
            @click="goToDetail(item.id)"
          />
        </template>

        <!-- 空状态 -->
        <el-empty v-if="!initialLoading && products.length === 0" description="暂无相关商品，快去抢首发吧！" class="empty-state" />
      </div>

      <!-- 加载更多指示器 -->
      <div v-if="!initialLoading && hasMore" class="load-more-area" ref="sentinelRef">
        <el-icon v-if="loadingMore" class="is-loading" :size="24"><Loading /></el-icon>
        <span v-else class="load-hint">上滑加载更多</span>
      </div>

      <!-- 已全部加载 -->
      <div v-if="!hasMore && products.length > 0" class="load-more-area">
        <span class="load-hint">— 已经到底了 —</span>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus, ArrowDown, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProductCard from '../components/ProductCard.vue'
import { getProducts, deleteProduct } from '../api/product'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const products = ref([])
const searchKeyword = ref('')
const initialLoading = ref(true)
const loadingMore = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const perPage = 12
const activeCategory = ref('')
const sentinelRef = ref(null)
let observer = null

const categories = [
  { label: '全部', value: '' },
  { label: '教材教辅', value: 'textbook' },
  { label: '电子数码', value: 'electronics' },
  { label: '生活日用', value: 'daily' },
  { label: '服饰鞋包', value: 'clothing' },
  { label: '运动户外', value: 'sports' },
  { label: '其他', value: 'other' },
]

const hasMore = computed(() => currentPage.value < totalPages.value)

// 构建查询参数
const buildParams = (page = 1) => {
  const params = { page, per_page: perPage }
  if (searchKeyword.value) params.keyword = searchKeyword.value
  if (activeCategory.value) params.category = activeCategory.value
  return params
}

// 获取商品（首页或刷新）
const fetchProducts = async () => {
  initialLoading.value = true
  currentPage.value = 1
  try {
    const res = await getProducts(buildParams(1))
    products.value = res.data
    totalPages.value = res.pagination.pages
  } catch (error) {
    // interceptor handles
  } finally {
    initialLoading.value = false
  }
}

// 加载更多（无限滚动）
const loadMore = async () => {
  if (!hasMore.value || loadingMore.value || initialLoading.value) return
  loadingMore.value = true
  currentPage.value++
  try {
    const res = await getProducts(buildParams(currentPage.value))
    products.value.push(...res.data)
    totalPages.value = res.pagination.pages
  } catch (error) {
    currentPage.value-- // rollback on error
  } finally {
    loadingMore.value = false
  }
}

// 搜索触发
const handleSearch = () => {
  activeCategory.value = ''
  fetchProducts()
}

// 分类筛选
const selectCategory = (value) => {
  activeCategory.value = value === activeCategory.value ? '' : value
  products.value = []
  fetchProducts()
}

// IntersectionObserver 无限滚动
const setupObserver = () => {
  if (!sentinelRef.value) return
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && hasMore.value && !loadingMore.value) {
      loadMore()
    }
  }, { rootMargin: '200px' })
  observer.observe(sentinelRef.value)
}

onMounted(() => {
  fetchProducts()
  // 延迟设置 observer 等 DOM 渲染完毕
  setTimeout(setupObserver, 500)
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
})

const goToPublish = () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push('/publish')
}
const goToDetail = (id) => router.push(`/product/${id}`)

const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'chat') {
    router.push('/chat')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
    }).then(() => {
      userStore.logout()
      ElMessage.success('已安全退出')
      fetchProducts()
    }).catch(() => {})
  }
}

const handleDeleteClick = (id) => {
  ElMessageBox.confirm('确定要下架并删除该商品吗？此操作不可恢复。', '警告', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
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

/* 顶部导航栏 */
.app-header {
  background-color: #ffffff;
  box-shadow: var(--box-shadow-base);
  position: sticky;
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
.brand { flex: 1; display: flex; align-items: center; }
.brand-text {
  font-size: 22px; font-weight: 600; color: var(--seu-green); letter-spacing: 1px;
}
.search-center { flex: 2; display: flex; justify-content: center; }
.large-search-input {
  width: 100%; max-width: 560px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03); border-radius: 4px;
}
.user-actions { flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 20px; }
.user-dropdown-link {
  cursor: pointer; color: var(--seu-black); display: flex; align-items: center;
  font-weight: 500; padding: 4px 8px; border-radius: 4px; transition: background-color 0.3s;
}
.user-dropdown-link:hover { background-color: #f4f6f8; }

/* 分类筛选 */
.category-filter {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}
.category-tag {
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
  transition: all 0.2s;
}
.category-tag:hover {
  transform: translateY(-1px);
}

/* 主内容区 */
.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 28px 24px 64px;
  box-sizing: border-box;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
  width: 100%;
  min-height: 400px;
}
.empty-state {
  grid-column: 1 / -1;
}

/* 骨架屏 */
.skeleton-card {
  border-radius: var(--border-radius-base);
  overflow: hidden;
  background: #fff;
  box-shadow: var(--box-shadow-base);
}

/* 加载区域 */
.load-more-area {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 32px 0 8px;
  grid-column: 1 / -1;
}
.load-hint {
  font-size: 14px;
  color: var(--text-light);
}
</style>
