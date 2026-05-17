<!-- src/views/ProductDetail.vue -->
<template>
  <div class="page-container">
    <!-- 顶部面包屑导航 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>商品详情</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 详情卡片主区块 -->
    <el-card class="detail-card" v-loading="loading">
      <div v-if="product" class="detail-layout">
        
        <!-- 左侧：商品大图 -->
        <div class="image-section">
          <el-image 
            :src="product.image_url" 
            :preview-src-list="[product.image_url]"
            fit="cover" 
            class="main-image">
            <template #error>
              <div class="image-error-slot">暂无图片</div>
            </template>
          </el-image>
        </div>

        <!-- 右侧：商品信息与操作区 -->
        <div class="info-section">
          <h1 class="product-title">{{ product.title }}</h1>
          
          <!-- 价格区块 (使用东南活力橙) -->
          <div class="price-box">
            <span class="currency">¥</span>
            <span class="price-number">{{ product.price }}</span>
          </div>

          <!-- 卖家信息卡片 -->
          <div class="seller-box">
            <div class="seller-label">发布者</div>
            <div class="seller-name">{{ product.seller_name }}</div>
            <div class="publish-time">发布于 {{ product.created_at }}</div>
          </div>

          <!-- 详细描述 -->
          <div class="description-box">
            <div class="desc-title">商品描述</div>
            <p class="desc-content">{{ product.description || '卖家很懒，没有留下描述' }}</p>
          </div>

          <!-- 底部操作区 (核心鉴权逻辑呈现) -->
          <div class="action-box">
            <template v-if="isSeller">
              <el-button 
                v-if="product.status === 'active'"
                type="danger" 
                size="large" 
                class="action-btn" 
                @click="handleDelete">
                下架并删除
              </el-button>
              <el-button v-else disabled size="large" class="action-btn">
                {{ product.status === 'sold' ? '该商品已售出' : '已下架' }}
              </el-button>
            </template>
            
            <template v-else>
              <el-button size="large" class="action-btn contact-btn" @click="handleContact">
                联系卖家
              </el-button>
              
              <!-- 购买按钮：加入状态判断与 loading -->
              <el-button 
                v-if="product.status === 'active'"
                type="primary" 
                size="large" 
                class="action-btn buy-btn" 
                :loading="buying"
                @click="handleBuy">
                立即购买
              </el-button>
              
              <!-- 售罄置灰按钮 -->
              <el-button 
                v-else 
                disabled 
                size="large" 
                class="action-btn">
                手慢了，已被抢购
              </el-button>
            </template>
          </div>
        </div>
      </div>
      
      <!-- 异常状态处理 -->
      <el-empty v-else-if="!loading" description="抱歉，商品已走丢~" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProductDetail, deleteProduct } from '../api/product'
import { useUserStore } from '../stores/user'
import { createOrder } from '../api/order'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const product = ref(null)
const loading = ref(true)
const buying = ref(false)

// 判断当前登录用户是否为卖家
const isSeller = computed(() => {
  if (!userStore.userInfo || !product.value) return false
  return userStore.userInfo.id === product.value.seller_id
})

// 初始化获取详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getProductDetail(route.params.id)
    product.value = res.data
  } catch (error) {
    // 接口报错 (如404下架)，拦截器会弹窗，随后退回首页
    setTimeout(() => router.replace('/'), 1500)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDetail()
})

// --- 按钮操作事件 ---

// 卖家删除操作
const handleDelete = () => {
  ElMessageBox.confirm('确定要下架并删除该商品吗？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteProduct(product.value.id)
      ElMessage.success('商品已下架')
      router.replace('/') // 删除后跳回首页
    } catch (error) {}
  }).catch(() => {})
}

// 买家购买操作
const handleBuy = async () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录后再进行购买')
    router.push('/login')
    return
  }
  
  try {
    buying.value = true
    const res = await createOrder({ product_id: product.value.id })
    ElMessage.success('购买成功！')
    // 购买成功后，路由跳转到个人中心的“我买到的”标签页
    router.replace('/profile?tab=bought')
  } catch (error) {
    // 异常拦截器会自动提取 msg 弹窗（如商品状态改变、不能购买自己的等）
    fetchDetail() // 刷新当前详情页以获取最新商品状态(例如已被别人买走)
  } finally {
    buying.value = false
  }
}

// 买家联系操作
const handleContact = () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录后再联系卖家')
    router.push('/login')
    return
  }
  
  // 防止联系自己发布的商品（逻辑保护）
  if (product.value.seller_id === userStore.userInfo?.id) {
    ElMessage.warning('不能联系自己！')
    return
  }

  // 携目标卖家 ID 跳转到聊天中心
  router.push({
    path: '/chat',
    query: { userId: product.value.seller_id }
  })
}
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 20px;
}

.detail-card {
  padding: 20px;
}

/* 采用 Grid 布局实现响应式的左右分栏 */
.detail-layout {
  display: grid;
  grid-template-columns: 45% 1fr;
  gap: 40px;
}

@media (max-width: 768px) {
  .detail-layout {
    grid-template-columns: 1fr; /* 移动端单列堆叠 */
  }
}

/* 左侧大图 */
.image-section {
  width: 100%;
  aspect-ratio: 1 / 1;
  background-color: #f5f7fa;
  border-radius: var(--border-radius-base);
  overflow: hidden;
}
.main-image {
  width: 100%;
  height: 100%;
  cursor: zoom-in; /* 提示可点击放大 */
}
.image-error-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-light);
}

/* 右侧信息区 */
.info-section {
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 24px;
  color: var(--seu-black);
  margin-top: 0;
  margin-bottom: 16px;
  line-height: 1.4;
}

.price-box {
  background-color: #fff9f0; /* 使用东南橙极浅色打底 */
  padding: 16px 20px;
  border-radius: var(--border-radius-base);
  margin-bottom: 24px;
}
.currency {
  font-size: 18px;
  color: var(--seu-orange);
  font-weight: bold;
  margin-right: 4px;
}
.price-number {
  font-size: 32px;
  color: var(--seu-orange);
  font-weight: bold;
}

/* 卖家信息块 */
.seller-box {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #f0f2f5;
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 24px;
}
.seller-label {
  color: var(--text-light);
  font-size: 14px;
  margin-right: 16px;
}
.seller-name {
  font-weight: 500;
  color: var(--seu-black);
  margin-right: auto; /* 将时间推向最右侧 */
}
.publish-time {
  font-size: 13px;
  color: var(--text-light);
}

/* 描述区块 */
.description-box {
  flex: 1; /* 占据剩余空间 */
  margin-bottom: 32px;
}
.desc-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--seu-black);
  margin-bottom: 12px;
}
.desc-content {
  font-size: 14px;
  line-height: 1.6;
  color: #555;
  white-space: pre-wrap; /* 保留用户输入的换行符 */
}

/* 底部操作区 */
.action-box {
  display: flex;
  gap: 16px;
}
.action-btn {
  flex: 1;
  font-size: 16px;
  font-weight: bold;
  border-radius: 8px; /* 圆角略大，更具现代感 */
}

/* 联系卖家按钮定制：使用东南绿镂空风格 */
.contact-btn {
  border-color: var(--seu-green) !important;
  color: var(--seu-green) !important;
  background-color: transparent !important;
}
.contact-btn:hover {
  background-color: rgba(88, 117, 88, 0.05) !important;
}

/* 购买按钮定制：保持主色填充不变，增加阴影提亮 */
.buy-btn {
  box-shadow: 0 4px 12px rgba(88, 117, 88, 0.3);
}
</style>