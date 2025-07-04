<template>
  <div class="gallery-container">
    <div v-if="dataStore.galleryItems.length === 0" class="empty-state">
      <p>Select points on the scatter plot to view detections</p>
    </div>
    
    <div v-else class="gallery-grid">
      <ImageItem
        v-for="item in dataStore.galleryItems"
        :key="item.annotation_id"
        :item="item"
        @toggle-check="dataStore.toggleItemCheck"
      />
    </div>

    <div v-if="dataStore.loading" class="loading-overlay">
      Loading images...
    </div>
  </div>
</template>

<script setup>
import ImageItem from './ImageItem.vue'
import { useDataStore } from '../stores/useDataStore'

const dataStore = useDataStore()
</script>

<style scoped>
.gallery-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-style: italic;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  padding: 16px;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: #666;
}
</style>