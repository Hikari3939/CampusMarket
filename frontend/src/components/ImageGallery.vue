<template>
  <div class="image-gallery">
    <div v-if="!images || images.length === 0" class="gallery-placeholder">
      <el-icon :size="48"><Picture /></el-icon>
      <span>暂无图片</span>
    </div>

    <template v-else-if="images.length === 1">
      <el-image
        :src="images[0]"
        :preview-src-list="images"
        fit="cover"
        class="gallery-single-image"
      >
        <template #error>
          <div class="image-error-slot">
            <el-icon :size="48"><Picture /></el-icon>
            <span>加载失败</span>
          </div>
        </template>
      </el-image>
    </template>

    <template v-else>
      <el-carousel :interval="5000" arrow="hover" indicator-position="outside" height="400px" class="gallery-carousel">
        <el-carousel-item v-for="(img, idx) in images" :key="idx">
          <el-image
            :src="img"
            :preview-src-list="images"
            :initial-index="idx"
            fit="cover"
            class="gallery-image"
          >
            <template #error>
              <div class="image-error-slot">
                <el-icon :size="48"><Picture /></el-icon>
                <span>加载失败</span>
              </div>
            </template>
          </el-image>
        </el-carousel-item>
      </el-carousel>
    </template>
  </div>
</template>

<script setup>
import { Picture } from '@element-plus/icons-vue'

defineProps({
  images: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.image-gallery {
  width: 100%;
  aspect-ratio: 1 / 1;
  background-color: #f5f7fa;
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.gallery-placeholder {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-light);
  gap: 8px;
  font-size: 14px;
}

.gallery-single-image {
  width: 100%;
  height: 100%;
  cursor: zoom-in;
}

.gallery-carousel {
  width: 100%;
  height: 100%;
}

.gallery-image {
  width: 100%;
  height: 100%;
  cursor: zoom-in;
}

.image-error-slot {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-light);
  gap: 8px;
  font-size: 14px;
}

:deep(.el-carousel__container) {
  height: 100% !important;
}

:deep(.el-carousel__item) {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
