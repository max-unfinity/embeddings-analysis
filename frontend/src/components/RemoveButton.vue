<template>
  <button 
    @click="handleRemove"
    :disabled="!canRemove || dataStore.loading"
    class="remove-button"
    :class="{ 'has-items': canRemove }"
  >
    <span v-if="dataStore.loading">Removing...</span>
    <span v-else>
      Remove {{ dataStore.checkedItems.length }} item{{ dataStore.checkedItems.length !== 1 ? 's' : '' }}
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useDataStore } from '../stores/useDataStore'

const dataStore = useDataStore()

const canRemove = computed(() => {
  return dataStore.checkedItems.length > 0
})

async function handleRemove() {
  if (!canRemove.value) return
  
  const confirmed = confirm(
    `Are you sure you want to remove ${dataStore.checkedItems.length} item(s)? This action cannot be undone.`
  )
  
  if (confirmed) {
    await dataStore.removeSelectedItems()
  }
}
</script>

<style scoped>
.remove-button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: not-allowed;
  transition: all 0.2s ease;
}

.remove-button.has-items {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
  cursor: pointer;
}

.remove-button.has-items:hover {
  background: #c82333;
  border-color: #bd2130;
  transform: translateY(-1px);
}

.remove-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>