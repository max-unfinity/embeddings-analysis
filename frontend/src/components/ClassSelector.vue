<template>
  <div class="class-selector">
    <label for="class-select" class="selector-label">
      Filter by class:
    </label>
    <select 
      id="class-select"
      v-model="dataStore.selectedClass"
      class="class-dropdown"
      :disabled="dataStore.loading"
    >
      <option 
        v-for="className in dataStore.classes" 
        :key="className"
        :value="className"
      >
        {{ className === 'all' ? 'All Classes' : className }}
      </option>
    </select>
  </div>
</template>

<script setup>
import { useDataStore } from '../stores/useDataStore'

const dataStore = useDataStore()
</script>

<style scoped>
.class-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selector-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.class-dropdown {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  min-width: 120px;
  cursor: pointer;
}

.class-dropdown:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.class-dropdown:focus {
  outline: none;
  border-color: #ff6600;
  box-shadow: 0 0 0 2px rgba(255, 102, 0, 0.2);
}
</style>