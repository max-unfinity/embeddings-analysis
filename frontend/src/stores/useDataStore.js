import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../services/api'

export const useDataStore = defineStore('data', () => {
  // State
  const embeddings = ref([])
  const classes = ref([])
  const selectedClass = ref('all')
  const selectedPoints = ref([])
  const galleryItems = ref([])
  const checkedItems = ref([])
  const loading = ref(false)

  // Computed
  const filteredEmbeddings = computed(() => {
    if (selectedClass.value === 'all') {
      return embeddings.value
    }
    return embeddings.value.filter(point => point.class_name === selectedClass.value)
  })

  // Actions
  async function loadEmbeddings() {
    loading.value = true
    try {
      const data = await api.getEmbeddings()
      embeddings.value = data
    } catch (error) {
      console.error('Failed to load embeddings:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadClassEmbeddings(className) {
    loading.value = true
    try {
      const data = await api.getEmbeddingsByClass(className)
      embeddings.value = data
      selectedClass.value = className
    } catch (error) {
      console.error('Failed to load class embeddings:', error)
    } finally {
      loading.value = false
    }
  }

  async function loadClasses() {
    try {
      const data = await api.getClasses()
      classes.value = ['all', ...data]
    } catch (error) {
      console.error('Failed to load classes:', error)
    }
  }

  async function updateSelection(selectionCoords) {
    try {
      const annotationIds = await api.getSelection(selectionCoords)
      selectedPoints.value = annotationIds
      
      // Load gallery items for selected points
      await loadGalleryItems(annotationIds)
    } catch (error) {
      console.error('Failed to update selection:', error)
    }
  }

  async function loadGalleryItems(annotationIds) {
    loading.value = true
    try {
      const items = annotationIds.map(id => ({
        annotation_id: id,
        imageUrl: api.getCropImageUrl(id),
        checked: false
      }))
      galleryItems.value = items
      checkedItems.value = []
    } catch (error) {
      console.error('Failed to load gallery items:', error)
    } finally {
      loading.value = false
    }
  }

  function toggleItemCheck(annotationId) {
    const item = galleryItems.value.find(item => item.annotation_id === annotationId)
    if (item) {
      item.checked = !item.checked
      if (item.checked) {
        checkedItems.value.push(annotationId)
      } else {
        checkedItems.value = checkedItems.value.filter(id => id !== annotationId)
      }
    }
  }

  async function removeSelectedItems() {
    if (checkedItems.value.length === 0) return
    
    loading.value = true
    try {
      await api.removeAnnotations(checkedItems.value)
      
      // Remove from current data
      embeddings.value = embeddings.value.filter(
        point => !checkedItems.value.includes(point.annotation_id)
      )
      galleryItems.value = galleryItems.value.filter(
        item => !checkedItems.value.includes(item.annotation_id)
      )
      selectedPoints.value = selectedPoints.value.filter(
        id => !checkedItems.value.includes(id)
      )
      
      checkedItems.value = []
    } catch (error) {
      console.error('Failed to remove items:', error)
    } finally {
      loading.value = false
    }
  }

  function clearSelection() {
    selectedPoints.value = []
    galleryItems.value = []
    checkedItems.value = []
  }

  return {
    // State
    embeddings,
    classes,
    selectedClass,
    selectedPoints,
    galleryItems,
    checkedItems,
    loading,
    
    // Computed
    filteredEmbeddings,
    
    // Actions
    loadEmbeddings,
    loadClassEmbeddings,
    loadClasses,
    updateSelection,
    loadGalleryItems,
    toggleItemCheck,
    removeSelectedItems,
    clearSelection
  }
})