<!-- src/views/ProductDetail.vue -->
<template>
  <div class="page-container">
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>商品详情</el-breadcrumb-item>
    </el-breadcrumb>

    <el-card class="detail-card" v-loading="loading">
      <div v-if="product" class="detail-layout">
        <div class="image-section">
          <ImageGallery :images="product.image_urls && product.image_urls.length ? product.image_urls : (product.image_url ? [product.image_url] : [])" />
        </div>

        <div class="info-section">
          <h1 class="product-title">{{ product.title }}</h1>

          <div class="price-box">
            <span class="currency">¥</span>
            <span class="price-number">{{ product.price }}</span>
          </div>

          <div class="seller-box">
            <div class="seller-label">发布者</div>
            <el-avatar :size="32" class="seller-avatar" @click="goToSeller">
              <img v-if="product.seller_avatar_url" :src="product.seller_avatar_url" style="width:100%;height:100%;object-fit:cover" />
            </el-avatar>
            <div class="seller-name" @click="goToSeller">
              {{ product.seller_name }}
            </div>
            <div class="publish-time">发布于 {{ product.created_at }}</div>
          </div>

          <div class="description-box">
            <div class="desc-title">商品描述</div>
            <p class="desc-content">{{ product.description || '卖家很懒，没有留下描述' }}</p>
          </div>

          <div class="action-box">
            <!-- 收藏按钮（非卖家可见） -->
            <el-button
              v-if="!isSeller && userStore.token"
              circle
              size="large"
              :type="detailFavorited ? 'danger' : 'default'"
              :icon="detailFavorited ? StarFilled : Star"
              @click="handleDetailToggleFavorite"
              class="fav-action-btn"
            />

            <template v-if="isSeller">
              <el-button
                v-if="product.status === 'active'"
                type="primary"
                size="large"
                class="action-btn"
                @click="openEditDialog">
                编辑商品
              </el-button>
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

              <el-button
                v-if="product.status === 'active'"
                type="primary"
                size="large"
                class="action-btn buy-btn"
                :loading="buying"
                @click="handleBuy">
                立即购买
              </el-button>

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

      <el-empty v-else-if="!loading" description="抱歉，商品已走丢~" />
    </el-card>

    <!-- 编辑商品对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑商品" width="600px" :close-on-click-modal="false">
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-position="top">
        <el-form-item label="商品标题" prop="title">
          <el-input v-model="editForm.title" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="商品分类" prop="category">
          <el-select v-model="editForm.category" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="价格(元)" prop="price">
          <el-input-number v-model="editForm.price" :min="0.01" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input v-model="editForm.description" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="更换图片 (最多5张)">
          <div class="edit-images-grid">
            <div v-for="(preview, idx) in editPreviewUrls" :key="'preview-'+idx" class="edit-preview-item">
              <img :src="preview" class="edit-preview-img" />
              <el-icon class="edit-preview-remove" @click="removeEditImage(idx)"><CircleClose /></el-icon>
            </div>
            <el-upload
              v-if="editSelectedFiles.length + product?.image_urls?.length < 5"
              class="image-uploader"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleEditImageChange"
              accept="image/png, image/jpeg, image/jpg, image/gif"
            >
              <el-icon class="uploader-icon"><Plus /></el-icon>
            </el-upload>
          </div>
          <div class="upload-tip">不选择新图片则不更换；选择后原图将全部替换</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="submitEdit">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, CircleClose, Star, StarFilled } from '@element-plus/icons-vue'
import { getProductDetail, deleteProduct, updateProduct } from '../api/product'
import { useUserStore } from '../stores/user'
import { createOrder } from '../api/order'
import { toggleFavorite, checkFavorites } from '../api/favorite'
import ImageGallery from '../components/ImageGallery.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const product = ref(null)
const loading = ref(true)
const buying = ref(false)
const detailFavorited = ref(false)

// Edit dialog state
const showEditDialog = ref(false)
const editFormRef = ref(null)
const editing = ref(false)
const editSelectedFiles = ref([])
const editPreviewUrls = ref([])
const editForm = reactive({ title: '', category: 'other', price: 0, description: '' })
const editRules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  price: [{ required: true, message: '请设置商品价格', trigger: 'blur' }],
  category: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
}

const categories = [
  { label: '教材教辅', value: 'textbook' },
  { label: '电子数码', value: 'electronics' },
  { label: '生活日用', value: 'daily' },
  { label: '服饰鞋包', value: 'clothing' },
  { label: '运动户外', value: 'sports' },
  { label: '其他', value: 'other' },
]

const isSeller = computed(() => {
  if (!userStore.userInfo || !product.value) return false
  return userStore.userInfo.id === product.value.seller_id
})

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getProductDetail(route.params.id)
    product.value = res.data
    // 检查收藏状态
    if (userStore.token && product.value) {
      try {
        const checkRes = await checkFavorites([product.value.id])
        detailFavorited.value = checkRes.data.includes(product.value.id)
      } catch (e) {}
    }
  } catch (error) {
    setTimeout(() => router.replace('/'), 1500)
  } finally {
    loading.value = false
  }
}

const handleDetailToggleFavorite = async () => {
  if (!product.value) return
  try {
    const res = await toggleFavorite(product.value.id)
    detailFavorited.value = res.data.is_favorited
    ElMessage.success(res.data.is_favorited ? '已添加收藏' : '已取消收藏')
  } catch (e) {}
}

onMounted(() => fetchDetail())

const goToSeller = () => {
  if (product.value?.seller_id) {
    router.push(`/user/${product.value.seller_id}`)
  }
}

const handleDelete = () => {
  ElMessageBox.confirm('确定要下架并删除该商品吗？', '警告', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning',
  }).then(async () => {
    try {
      await deleteProduct(product.value.id)
      ElMessage.success('商品已下架')
      router.replace('/')
    } catch (error) {}
  }).catch(() => {})
}

const handleBuy = async () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录后再进行购买')
    router.push('/login')
    return
  }
  try {
    buying.value = true
    await createOrder({ product_id: product.value.id })
    ElMessage.success('购买成功！')
    router.replace('/profile?tab=bought')
  } catch (error) {
    fetchDetail()
  } finally {
    buying.value = false
  }
}

const handleContact = () => {
  if (!userStore.token) {
    ElMessage.warning('请先登录后再联系卖家')
    router.push('/login')
    return
  }
  if (product.value.seller_id === userStore.userInfo?.id) {
    ElMessage.warning('不能联系自己！')
    return
  }
  router.push({ path: '/chat', query: { userId: product.value.seller_id } })
}

// --- Edit dialog logic ---
const openEditDialog = () => {
  if (!product.value) return
  editForm.title = product.value.title
  editForm.category = product.value.category || 'other'
  editForm.price = product.value.price
  editForm.description = product.value.description || ''
  editSelectedFiles.value = []
  editPreviewUrls.value = []
  showEditDialog.value = true
}

const handleEditImageChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  if (file.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  const totalCount = editSelectedFiles.value.length + (product.value?.image_urls?.length || 0)
  if (totalCount >= 5) {
    ElMessage.warning('最多只能上传 5 张图片')
    return false
  }
  editSelectedFiles.value.push(file)
  editPreviewUrls.value.push(URL.createObjectURL(file))
}

const removeEditImage = (idx) => {
  editSelectedFiles.value.splice(idx, 1)
  URL.revokeObjectURL(editPreviewUrls.value[idx])
  editPreviewUrls.value.splice(idx, 1)
}

const submitEdit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (valid) => {
    if (!valid) return
    editing.value = true
    const formData = new FormData()
    formData.append('title', editForm.title)
    formData.append('category', editForm.category)
    formData.append('price', editForm.price)
    formData.append('description', editForm.description)
    if (editSelectedFiles.value.length > 0) {
      editSelectedFiles.value.forEach((file, idx) => {
        formData.append(`image_${idx}`, file)
      })
    }
    try {
      const res = await updateProduct(product.value.id, formData)
      product.value = res.data
      ElMessage.success('商品更新成功')
      showEditDialog.value = false
    } catch (error) {
      // handled by interceptor
    } finally {
      editing.value = false
    }
  })
}
</script>

<style scoped>
.breadcrumb { margin-bottom: 20px; }
.detail-card { padding: 20px; }
.detail-layout { display: grid; grid-template-columns: 45% 1fr; gap: 40px; }
@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; }
}
.image-section {
  width: 100%; aspect-ratio: 1 / 1;
  background-color: #f5f7fa; border-radius: var(--border-radius-base); overflow: hidden;
}
.main-image { width: 100%; height: 100%; cursor: zoom-in; }
.image-error-slot {
  display: flex; justify-content: center; align-items: center;
  height: 100%; color: var(--text-light);
}
.info-section { display: flex; flex-direction: column; }
.product-title {
  font-size: 24px; color: var(--seu-black); margin-top: 0; margin-bottom: 16px; line-height: 1.4;
}
.price-box {
  background-color: #fff9f0; padding: 16px 20px;
  border-radius: var(--border-radius-base); margin-bottom: 24px;
}
.currency { font-size: 18px; color: var(--seu-orange); font-weight: bold; margin-right: 4px; }
.price-number { font-size: 32px; color: var(--seu-orange); font-weight: bold; }
.seller-box {
  display: flex; align-items: center; padding: 12px 0;
  border-top: 1px solid #f0f2f5; border-bottom: 1px solid #f0f2f5; margin-bottom: 24px;
}
.seller-label { color: var(--text-light); font-size: 14px; margin-right: 16px; }
.seller-avatar {
  cursor: pointer; flex-shrink: 0; background-color: var(--seu-green);
}
.seller-name {
  font-weight: 500; color: var(--seu-green); margin-right: auto; cursor: pointer;
  transition: opacity 0.2s;
}
.seller-name:hover { opacity: 0.7; }
.publish-time { font-size: 13px; color: var(--text-light); }
.description-box { flex: 1; margin-bottom: 32px; }
.desc-title { font-size: 16px; font-weight: 500; color: var(--seu-black); margin-bottom: 12px; }
.desc-content { font-size: 14px; line-height: 1.6; color: #555; white-space: pre-wrap; }
.action-box { display: flex; gap: 16px; }
.action-btn { flex: 1; font-size: 16px; font-weight: bold; border-radius: 8px; }
.contact-btn {
  border-color: var(--seu-green) !important; color: var(--seu-green) !important;
  background-color: transparent !important;
}
.contact-btn:hover { background-color: rgba(88, 117, 88, 0.05) !important; }
.buy-btn { box-shadow: 0 4px 12px rgba(88, 117, 88, 0.3); }

/* Edit dialog image uploader */
.image-uploader {
  border: 1px dashed #d9d9d9; border-radius: 6px; cursor: pointer; overflow: hidden;
  width: 178px; height: 178px; display: flex; justify-content: center; align-items: center;
  background-color: #fafafa; transition: var(--el-transition-duration-fast);
}
.image-uploader:hover { border-color: var(--seu-green); }
.uploader-icon { font-size: 28px; color: #8c939d; }
.preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }
.upload-tip { font-size: 12px; color: var(--text-light); margin-top: 8px; }

/* 多图编辑网格 */
.edit-images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-start;
}
.edit-preview-item {
  position: relative;
  width: 88px;
  height: 88px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #d9d9d9;
}
.edit-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.edit-preview-remove {
  position: absolute;
  top: -4px;
  right: -4px;
  font-size: 18px;
  color: #F56C6C;
  cursor: pointer;
  background: white;
  border-radius: 50%;
}
.image-uploader {
  border: 1px dashed #d9d9d9; border-radius: 6px; cursor: pointer; overflow: hidden;
  width: 88px; height: 88px; display: flex; justify-content: center; align-items: center;
  background-color: #fafafa; transition: var(--el-transition-duration-fast);
}
.image-uploader:hover { border-color: var(--seu-green); }
.uploader-icon { font-size: 28px; color: #8c939d; }
.preview-img { width: 100%; height: 100%; object-fit: cover; display: block; }
</style>
