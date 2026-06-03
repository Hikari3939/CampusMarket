<!-- src/views/Publish.vue -->
<template>
  <div class="page-container">
    <el-card class="publish-card">
      <h2 class="page-title">发布闲置</h2>

      <!-- 上传进度条 -->
      <el-progress
        v-if="uploadPercent > 0 && uploadPercent < 100"
        :percentage="uploadPercent"
        :stroke-width="6"
        color="var(--seu-green)"
        style="margin-bottom: 20px;"
      />

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        label-position="top">

        <el-form-item label="商品标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入商品名称，如：九成新高数教材" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="商品分类" prop="category">
          <el-select v-model="form.category" placeholder="请选择商品分类" style="width: 100%">
            <el-option
              v-for="cat in categories"
              :key="cat.value"
              :label="cat.label"
              :value="cat.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品价格 (元)" prop="price">
          <el-input-number v-model="form.price" :min="0.01" :precision="2" :step="1" placeholder="0.00" style="width: 100%" />
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="详细描述一下你的商品（新旧程度、购买时间等）"
            maxlength="500"
            show-word-limit />
        </el-form-item>

        <el-form-item label="商品图片 (最多5张)" prop="image">
          <div class="publish-images-grid">
            <div v-for="(preview, idx) in previewUrls" :key="'pub-preview-'+idx" class="publish-preview-item">
              <img :src="preview" class="publish-preview-img" />
              <el-icon class="publish-preview-remove" @click="removePublishImage(idx)"><CircleClose /></el-icon>
            </div>
            <el-upload
              v-if="selectedFiles.length < 5"
              class="image-uploader"
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleImageChange"
              accept="image/png, image/jpeg, image/jpg, image/gif"
            >
              <el-icon class="uploader-icon"><Plus /></el-icon>
            </el-upload>
          </div>
          <div class="upload-tip">建议上传 1:1 比例的高清图片，单张不超过 5MB，最多 5 张。</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" @click="submitForm" :loading="submitting">
            确认发布
          </el-button>
          <el-button size="large" @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, CircleClose } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createProduct } from '../api/product'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const uploadPercent = ref(0)

// 分类选项
const categories = [
  { label: '教材教辅', value: 'textbook' },
  { label: '电子数码', value: 'electronics' },
  { label: '生活日用', value: 'daily' },
  { label: '服饰鞋包', value: 'clothing' },
  { label: '运动户外', value: 'sports' },
  { label: '其他', value: 'other' },
]

// 表单数据
const form = reactive({
  title: '',
  category: 'other',
  price: undefined,
  description: '',
})

// 图片相关
const selectedFiles = ref([])
const previewUrls = ref([])

// 表单校验规则
const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  price: [{ required: true, message: '请设置商品价格', trigger: 'blur' }],
  category: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
}

// 处理图片选择与本地预览
const handleImageChange = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  if (file.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  if (selectedFiles.value.length >= 5) {
    ElMessage.warning('最多只能上传 5 张图片')
    return false
  }
  selectedFiles.value.push(file)
  previewUrls.value.push(URL.createObjectURL(file))
}

// 移除待上传图片
const removePublishImage = (idx) => {
  selectedFiles.value.splice(idx, 1)
  URL.revokeObjectURL(previewUrls.value[idx])
  previewUrls.value.splice(idx, 1)
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (selectedFiles.value.length === 0) {
        ElMessage.warning('请至少上传一张商品图片')
        return
      }

      submitting.value = true
      uploadPercent.value = 0

      // 构建 FormData
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('price', form.price)
      formData.append('category', form.category)
      formData.append('description', form.description)
      // 以 image_0, image_1... 格式发送多图
      selectedFiles.value.forEach((file, idx) => {
        formData.append(`image_${idx}`, file)
      })

      try {
        await createProduct(formData, {
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              uploadPercent.value = Math.round((progressEvent.loaded / progressEvent.total) * 100)
            }
          }
        })
        ElMessage.success('发布成功！')
        router.push('/')
      } catch (error) {
        // Axios 拦截器已处理报错
      } finally {
        submitting.value = false
        uploadPercent.value = 0
      }
    }
  })
}
</script>

<style scoped>
.publish-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.page-title {
  color: var(--seu-black);
  margin-bottom: 24px;
  text-align: center;
}
/* 多图上传网格 */
.publish-images-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-start;
}
.publish-preview-item {
  position: relative;
  width: 128px;
  height: 128px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #d9d9d9;
}
.publish-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.publish-preview-remove {
  position: absolute;
  top: -4px;
  right: -4px;
  font-size: 20px;
  color: #F56C6C;
  cursor: pointer;
  background: white;
  border-radius: 50%;
}
.image-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 128px;
  height: 128px;
  transition: var(--el-transition-duration-fast);
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fafafa;
}
.image-uploader:hover {
  border-color: var(--seu-green);
}
.uploader-icon {
  font-size: 28px;
  color: #8c939d;
}
.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.upload-tip {
  font-size: 12px;
  color: var(--text-light);
  margin-top: 8px;
}
</style>
