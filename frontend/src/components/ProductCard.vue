<template>
  <el-card class="product-card" :body-style="{ padding: '0px' }">
    <!-- 商品主图 -->
    <div class="image-wrapper">
      <el-image
        :src="product.image_url"
        fit="cover"
        class="product-image"
        lazy>
        <template #error>
          <div class="image-slot">
            <el-icon><Picture /></el-icon>
            <span>暂无图片</span>
          </div>
        </template>
      </el-image>
      <!-- 收藏按钮 -->
      <div class="fav-btn" v-if="userStore.token" @click.stop="handleToggleFavorite">
        <el-icon :size="20" :color="isFavorited ? '#F56C6C' : '#ccc'">
          <StarFilled v-if="isFavorited" />
          <Star v-else />
        </el-icon>
      </div>
    </div>

    <!-- 商品信息 -->
    <div class="product-info">
      <h3 class="title el-input__inner">{{ product.title }}</h3>
      <p class="desc">{{ product.description || '卖家很懒，没有留下描述' }}</p>
      
      <div class="bottom-bar">
        <span class="text-price">¥ {{ product.price }}</span>
        <span class="seller-name" @click.stop="goToSeller">
          <el-avatar :size="20" class="seller-mini-avatar">
            <img v-if="product.seller_avatar_url" :src="product.seller_avatar_url" style="width:100%;height:100%;object-fit:cover" />
          </el-avatar>
          {{ product.seller_name }}
        </span>
      </div>

      <!-- 删除按钮，仅当当前登录用户是卖家时显示 -->
      <div class="action-bar" v-if="isSeller">
        <el-button type="danger" text @click.stop="handleDelete">下架删除</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Picture, Star, StarFilled } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { toggleFavorite, checkFavorites } from '../api/favorite'

const router = useRouter()

const props = defineProps({
  product: { type: Object, required: true }
})
const emit = defineEmits(['delete'])

const userStore = useUserStore()
const isFavorited = ref(false)

// 判断当前商品是否为当前登录用户发布
const isSeller = computed(() => {
  return userStore.userInfo && userStore.userInfo.id === props.product.seller_id
})

const goToSeller = () => {
  router.push(`/user/${props.product.seller_id}`)
}

const handleDelete = () => {
  emit('delete', props.product.id)
}

const handleToggleFavorite = async () => {
  try {
    const res = await toggleFavorite(props.product.id)
    isFavorited.value = res.data.is_favorited
  } catch (e) {
    // handled by interceptor
  }
}

// 检查收藏状态
onMounted(async () => {
  if (userStore.token && props.product.id) {
    try {
      const res = await checkFavorites([props.product.id])
      isFavorited.value = res.data.includes(props.product.id)
    } catch (e) {}
  }
})
</script>

<style scoped>
.product-card {
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.image-wrapper {
  width: 100%;
  padding-top: 100%; /* 1:1 占位 */
  position: relative;
  background-color: #fafafa;
}
.product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
.image-slot {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-light);
  font-size: 14px;
}
.product-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.title {
  font-size: 16px;
  color: var(--text-main);
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.desc {
  font-size: 13px;
  color: var(--text-light);
  margin-bottom: 16px;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}
.bottom-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.seller-name {
  font-size: 12px;
  color: var(--text-light);
  background-color: #f0f2f5;
  padding: 2px 8px 2px 4px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.seller-mini-avatar {
  flex-shrink: 0;
}
.action-bar {
  margin-top: 12px;
  border-top: 1px dashed #ebeef5;
  padding-top: 8px;
  text-align: right;
}

.fav-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.9);
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.2s;
}
.fav-btn:hover {
  transform: scale(1.15);
}
</style>