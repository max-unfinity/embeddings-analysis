import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Embeddings endpoints
export async function getEmbeddings() {
  const response = await api.get('/embeddings')
  return response.data
}

export async function getEmbeddingsByClass(className) {
  const response = await api.get(`/embeddings/${className}`)
  return response.data
}

// Classes endpoint
export async function getClasses() {
  const response = await api.get('/classes')
  return response.data
}

// Selection endpoint
export async function getSelection(selectionCoords) {
  const response = await api.post('/selection', selectionCoords)
  return response.data.annotation_ids
}

// Image endpoints
export function getCropImageUrl(annotationId) {
  return `${API_BASE_URL}/crop/${annotationId}`
}

// Remove annotations endpoint
export async function removeAnnotations(annotationIds) {
  const response = await api.post('/remove', { 
    annotation_ids: annotationIds 
  })
  return response.data
}

export default api