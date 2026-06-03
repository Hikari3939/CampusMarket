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
        <el-avatar :size="72" class="user-avatar">
          <img v-if="profileUser.avatar_url" :src="profileUser.avatar_url" style="width:100%;height:100%;object-fit:cover" />
          <span v-else>{{ profileUser.username.charAt(0) }}</span>
        </el-avatar>
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

    <!-- 评价摘要 -->
    <div class="reviews-summary" v-if="profileUser && (profileUser.avg_rating > 0 || profileUser.review_count > 0)">
      <div class="reviews-header">
        <h3>信誉评价</h3>
      </div>
      <div class="reviews-stats">
        <StarRating :model-value="profileUser.avg_rating" readonly :count="profileUser.review_count" :show-count="true" />
      </div>
      <!-- 详细评价列表 -->
      <div class="reviews-list" v-if="reviews.length > 0">
        <div v-for="r in reviews" :key="r.id" class="review-item">
          <div class="review-top">
            <el-avatar :size="28" class="review-avatar">
              <img v-if="r.reviewer.avatar_url" :src="r.reviewer.avatar_url" style="width:100%;height:100%;object-fit:cover" />
            </el-avatar>
            <span class="reviewer-name">{{ r.reviewer.username }}</span>
            <StarRating :model-value="r.rating" readonly />
            <span class="review-time">{{ r.created_at }}</span>
          </div>
          <p class="review-comment" v-if="r.comment">{{ r.comment }}</p>
        </div>
      </div>
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
import { getUserReviews } from '../api/review'
import { useUserStore } from '../stores/user'
import ProductCard from '../components/ProductCard.vue'
import StarRating from '../components/StarRating.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const profileUser = ref(null)
const products = ref([])
const reviews = ref([])
const loading = ref(true)

const fetchProfile = async () => {
  loading.value = true
  try {
    const res = await getUserProfile(route.params.id)
    profileUser.value = res.data.user
    products.value = res.data.products

    // 拉取评价
    try {
      const reviewRes = await getUserReviews(route.params.id)
      reviews.value = reviewRes.data.reviews
    } catch (e) {}
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

/* 评价摘要 */
.reviews-summary {
  margin-bottom: 32px;
  padding: 20px 0;
  border-top: 1px solid #f0f2f5;
}
.reviews-header h3 {
  font-size: 18px;
  color: var(--seu-black);
  margin-bottom: 12px;
}
.reviews-stats {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.review-item {
  padding: 14px 16px;
  background: #fafbfc;
  border-radius: 8px;
}
.review-top {
  display: flex;
  align-items: center;
  gap: 10px;
}
.review-avatar {
  background-color: var(--seu-green);
  font-size: 12px;
}
.reviewer-name {
  font-weight: 500;
  color: var(--seu-black);
  font-size: 14px;
}
.review-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-light);
}
.review-comment {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-main);
  line-height: 1.5;
}

/* dark mode */
html.dark .review-item {
  background-color: #1a1a2e;
}
html.dark .reviews-summary {
  border-top-color: #2a2a4a;
}
html.dark .reviews-header h3 {
  color: #e0e0e0;
}
</style>
