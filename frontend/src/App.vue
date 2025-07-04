<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <h1>Object Detection Analysis Tool</h1>
      <div class="header-controls">
        <ClassSelector />
        <RemoveButton />
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <!-- Left Panel: Scatter Plot -->
      <div class="left-panel">
        <div class="panel-header">
          <h2>Embedding Visualization</h2>
          <div class="selection-info">
            Selected: {{ dataStore.selectedPoints.length }} points
          </div>
        </div>
        <ScatterPlot />
      </div>

      <!-- Right Panel: Gallery -->
      <div class="right-panel">
        <div class="panel-header">
          <h2>Detection Gallery</h2>
          <div class="gallery-info">
            {{ dataStore.galleryItems.length }} items
            ({{ dataStore.checkedItems.length }} selected for removal)
          </div>
        </div>
        <Gallery />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import ScatterPlot from './components/ScatterPlot.vue'
import Gallery from './components/Gallery.vue'
import ClassSelector from './components/ClassSelector.vue'
import RemoveButton from './components/RemoveButton.vue'
import { useDataStore } from './stores/useDataStore'

const dataStore = useDataStore()

onMounted(() => {
  dataStore.loadEmbeddings()
  dataStore.loadClasses()
})
</script>