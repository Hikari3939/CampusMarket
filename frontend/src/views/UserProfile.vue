<!-- src/views/UserProfile.vue -->
<template>
  <div class="page-container">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>{{ profileUser?.username }} 的主页</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 用户信息头部 -->
    <div class="user-header" v-loading="loading">
      <template v-if="profileUser">
        <el-avatar :size="72" class="user-avatar">{{ profileUser.username.charAt(0) }}</el-avatar>
        <div class="user-meta">
          <h2>{{ profileUser.username }}</h2>
          <p>加入于 {{ profileUser.created_at }}</p>
        </div>
        <el-button
          v-if="userStore.token && userStore.userInfo?.id !== profileUser.id"
          type="primary"
          :icon="ChatDotRound"
          @click="contactSeller"
          style="margin-left: auto;">
          联系 TA
        </el-button>
      </template>
    </div>

    <!-- 在售商品 -->
    <h3 class="section-title" v-if="products.length > 0">
      TA 的在售商品 ({{ products.length }})
    </h3>

    <div class="product-grid" v-loading="loading">
      <ProductCard
        v-for="item in products"
        :key="item.id"
        :product="item"
        @click="goToDetail(item.id)"
      />
      <el-empty v-if="!loading && products.length === 0" description="TA 暂无在售商品" class="empty-state" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChatDotRound } from '@element-plus/icons-vue'
import { getUserProfile } from '../api/user'
import { useUserStore } from '../stores/user'
import ProductCard from '../components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const profileUser = ref(null)
const products = ref([])
const loading = ref(true)

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await getUserProfile(route.params.id)
    profileUser.value = res.data.user
    products.value = res.data.products
  } catch (error) {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => router.push(`/product/${id}`)

const contactSeller = () => {
  if (!userStore.token) {
    router.push('/login')
    return
  }
  router.push({ path: '/chat', query: { userId: profileUser.value.id } })
}

onMounted(() => fetchProfile())
</script>

<style scoped>
.breadcrumb { margin-bottom: 20px; }

.user-header {
  display: flex;
  align-items: center;
  padding: 32px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #f0f2f5;
}
.user-avatar {
  background-color: var(--seu-green);
  font-size: 28px;
  font-weight: bold;
}
.user-meta { margin-left: 24px; flex: 1; }
.user-meta h2 { color: var(--seu-black); margin-bottom: 8px; font-size: 22px; }
.user-meta p { color: var(--text-light); font-size: 14px; }

.section-title {
  font-size: 18px;
  color: var(--seu-black);
  margin-bottom: 20px;
  font-weight: 500;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
  width: 100%;
  min-height: 200px;
}
.empty-state {
  grid-column: 1 / -1;
}
</style>
