<template>
  <div class="image-item" :class="{ checked: item.checked }">
    <div class="image-wrapper">
      <img 
        :src="item.imageUrl" 
        :alt="`Detection ${item.annotation_id}`"
        @load="handleImageLoad"
        @error="handleImageError"
        class="detection-image"
      />
      <div v-if="loading" class="image-loading">
        Loading...
      </div>
      <div v-if="error" class="image-error">
        Failed to load
      </div>
    </div>
    
    <div class="item-controls">
      <label class="checkbox-wrapper">
        <input 
          type="checkbox" 
          :checked="item.checked"
          @change="handleToggle"
          class="item-checkbox"
        />
        <span class="checkbox-label">
          ID: {{ item.annotation_id }}
        </span>
      </label>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['toggle-check'])

const loading = ref(true)
const error = ref(false)

function handleToggle() {
  emit('toggle-check', props.item.annotation_id)
}

function handleImageLoad() {
  loading.value = false
  error.value = false
}

function handleImageError() {
  loading.value = false
  error.value = true
}
</script>

<style scoped>
.image-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  background: white;
  transition: all 0.2s ease;
  cursor: pointer;
}

.image-item:hover {
  border-color: #bbb;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.image-item.checked {
  border-color: #ff6600;
  background: #fff7f0;
}

.image-wrapper {
  position: relative;
  width: 100%;
  height: 100px;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detection-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.image-loading,
.image-error {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  color: #666;
}

.image-error {
  color: #d32f2f;
}

.item-controls {
  margin-top: 8px;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 12px;
}

.item-checkbox {
  margin-right: 6px;
  accent-color: #ff6600;
}

.checkbox-label {
  color: #666;
  font-weight: 500;
}

.image-item.checked .checkbox-label {
  color: #ff6600;
}
</style>