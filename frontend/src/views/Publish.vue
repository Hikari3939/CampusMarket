<!-- src/views/Publish.vue -->
<template>
  <div class="page-container">
    <el-card class="publish-card">
      <h2 class="page-title">发布闲置</h2>
      
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="top">
        
        <el-form-item label="商品标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入商品名称，如：九成新高数教材" maxlength="50" show-word-limit />
        </el-form-item>

        <el-form-item label="商品价格 (元)" prop="price">
          <el-input-number v-model="form.price" :min="0.01" :precision="2" :step="1" placeholder="0.00" />
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

        <el-form-item label="商品图片" prop="image">
          <!-- 注意：auto-upload="false" 阻止自动上传，改为随表单一起提交 -->
          <el-upload
            class="image-uploader"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleImageChange"
            accept="image/png, image/jpeg, image/jpg, image/gif"
          >
            <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
            <el-icon v-else class="uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">建议上传 1:1 比例的高清图片，大小不超过 5MB。</div>
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
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createProduct } from '../api/product'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

// 表单数据
const form = reactive({
  title: '',
  price: undefined,
  description: '',
})

// 图片相关
const selectedFile = ref(null)
const previewUrl = ref('')

// 表单校验规则
const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  price: [{ required: true, message: '请设置商品价格', trigger: 'blur' }]
}

// 处理图片选择与本地预览
const handleImageChange = (uploadFile) => {
  const file = uploadFile.raw
  if (file.size / 1024 / 1024 > 5) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file) // 生成本地预览图
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      if (!selectedFile.value) {
        ElMessage.warning('请上传一张商品图片')
        return
      }

      submitting.value = true
      
      // 【重点】：构建 FormData
      const formData = new FormData()
      formData.append('title', form.title)
      formData.append('price', form.price)
      formData.append('description', form.description)
      formData.append('image', selectedFile.value)

      try {
        await createProduct(formData)
        ElMessage.success('发布成功！')
        router.push('/') // 返回首页
      } catch (error) {
        // Axios 拦截器已处理报错
      } finally {
        submitting.value = false
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
.image-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
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