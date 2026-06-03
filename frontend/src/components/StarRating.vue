<template>
  <div class="star-rating" :class="{ readonly }">
    <span
      v-for="i in 5"
      :key="i"
      class="star"
      :class="{ filled: i <= displayValue }"
      @click="handleClick(i)"
      @mouseenter="handleHover(i)"
      @mouseleave="handleLeave"
    >&#9733;</span>
    <span v-if="showCount && count > 0" class="rating-count">({{ count }})</span>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },
  readonly: { type: Boolean, default: false },
  count: { type: Number, default: 0 },
  showCount: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const hoverRating = ref(0)

const displayValue = computed(() => {
  if (props.readonly) return Math.round(props.modelValue)
  return hoverRating.value || props.modelValue
})

const handleClick = (i) => {
  if (props.readonly) return
  emit('update:modelValue', i)
}

const handleHover = (i) => {
  if (props.readonly) return
  hoverRating.value = i
}

const handleLeave = () => {
  if (props.readonly) return
  hoverRating.value = 0
}
</script>

<style scoped>
.star-rating {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.star {
  font-size: 24px;
  color: #ddd;
  cursor: pointer;
  transition: color 0.15s, transform 0.15s;
  user-select: none;
}

.star.filled {
  color: #F6AB00;
}

.star-rating:not(.readonly) .star:hover {
  transform: scale(1.2);
}

.star-rating.readonly .star {
  cursor: default;
}

.rating-count {
  margin-left: 6px;
  font-size: 14px;
  color: var(--text-light);
}
</style>
