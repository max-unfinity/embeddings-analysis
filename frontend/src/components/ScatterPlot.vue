<template>
  <div class="scatter-plot-container">
    <div ref="chartRef" class="chart"></div>
    <div v-if="dataStore.loading" class="loading-overlay">
      Loading embeddings...
    </div>
    <div class="plot-controls">
      <button @click="resetZoom" class="reset-button" :disabled="dataStore.loading">
        Reset View
      </button>
      <div class="controls-info">
        Right-click + drag to pan • Mouse wheel to zoom
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as d3 from 'd3'
import { useDataStore } from '../stores/useDataStore'

const chartRef = ref(null)
const dataStore = useDataStore()

let svg, g, xScale, yScale, brush, zoom, originalXDomain, originalYDomain
let classColorMap = new Map()
let width, height, resizeObserver

const margin = { top: 20, right: 20, bottom: 40, left: 40 }

// Generate random color for a class
function generateRandomColor() {
  const hue = Math.random() * 360
  const saturation = 65 + Math.random() * 20 // 65-85%
  const lightness = 45 + Math.random() * 20  // 45-65%
  return `hsl(${hue}, ${saturation}%, ${lightness}%)`
}

function getColor(className) {
  if (!classColorMap.has(className)) {
    classColorMap.set(className, generateRandomColor())
  }
  return classColorMap.get(className)
}

// Get container dimensions and account for margins
function getContainerDimensions() {
  if (!chartRef.value) return { width: 600, height: 400 }
  
  const rect = chartRef.value.getBoundingClientRect()
  
  // If container has no size yet, try to get it from parent or use defaults
  let containerWidth = rect.width
  let containerHeight = rect.height
  
  if (containerWidth === 0 || containerHeight === 0) {
    const parent = chartRef.value.parentElement
    if (parent) {
      const parentRect = parent.getBoundingClientRect()
      containerWidth = parentRect.width || 600
      containerHeight = parentRect.height || 400
    } else {
      containerWidth = 600
      containerHeight = 400
    }
  }
  
  return {
    width: Math.max(300, containerWidth - margin.left - margin.right),
    height: Math.max(250, containerHeight - margin.top - margin.bottom)
  }
}

function updateDimensions() {
  const dimensions = getContainerDimensions()
  width = dimensions.width
  height = dimensions.height
}

let resizeTimeout

function setupResizeObserver() {
  if (!window.ResizeObserver) {
    // Fallback to window resize for older browsers
    window.addEventListener('resize', handleResize)
    return
  }
  
  resizeObserver = new ResizeObserver(() => {
    // Debounce resize events
    clearTimeout(resizeTimeout)
    resizeTimeout = setTimeout(() => {
      const oldWidth = width
      const oldHeight = height
      updateDimensions()
      
      // Only resize if dimensions actually changed
      if (svg && (width !== oldWidth || height !== oldHeight)) {
        resizeChart()
      }
    }, 100)
  })
  
  if (chartRef.value) {
    resizeObserver.observe(chartRef.value)
  }
}

function handleResize() {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    const oldWidth = width
    const oldHeight = height
    updateDimensions()
    
    if (svg && (width !== oldWidth || height !== oldHeight)) {
      resizeChart()
    }
  }, 100)
}

function resizeChart() {
  if (!svg) return
  
  // Update SVG dimensions
  svg
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  
  // Update clip path
  svg.select("#plot-clip rect")
    .attr("width", width)
    .attr("height", height)
  
  // Update axis positions
  g.select(".x-axis")
    .attr("transform", `translate(0,${height})`)
  
  // Update zoom extent
  if (zoom) {
    zoom.extent([[0, 0], [width, height]])
    svg.call(zoom)
  }
  
  // Update brush extent
  if (brush) {
    brush.extent([[0, 0], [width, height]])
    g.select(".brush").call(brush)
  }
  
  // Recalculate and update chart
  updateChart()
}

function initChart() {
  // Clear existing chart
  d3.select(chartRef.value).selectAll("*").remove()

  // Update dimensions from container
  updateDimensions()

  svg = d3.select(chartRef.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)

  // Create main group for content
  g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`)

  // Add clipping rectangle
  svg.append("defs").append("clipPath")
    .attr("id", "plot-clip")
    .append("rect")
    .attr("width", width)
    .attr("height", height)

  // Create zoom behavior
  zoom = d3.zoom()
    .scaleExtent([0.1, 10])
    .extent([[0, 0], [width, height]])
    .on("zoom", handleZoom)
    .filter(event => {
      // Allow zoom with wheel, pan with right mouse button
      return event.type === 'wheel' || (event.type === 'mousedown' && event.button === 2)
    })

  // Apply zoom to SVG and disable context menu on right-click
  svg.call(zoom)
    .on("contextmenu", event => event.preventDefault())

  // Add axes groups
  g.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height})`)

  g.append("g")
    .attr("class", "y-axis")

  // Create points container with clipping
  g.append("g")
    .attr("class", "points-container")
    .attr("clip-path", "url(#plot-clip)")

  // Add brush for selection (on top of everything)
  brush = d3.brush()
    .extent([[0, 0], [width, height]])
    .on("end", handleBrushEnd)
    .filter(event => {
      // Only allow brush with left mouse button
      return event.type !== 'mousedown' || event.button === 0
    })

  g.append("g")
    .attr("class", "brush")
    .call(brush)
}

function updateChart() {
  if (!svg || !dataStore.filteredEmbeddings.length) return

  const data = dataStore.filteredEmbeddings

  // Calculate base scales
  const xExtent = d3.extent(data, d => d.x)
  const yExtent = d3.extent(data, d => d.y)

  // Add some padding to the domains
  const xPadding = (xExtent[1] - xExtent[0]) * 0.05
  const yPadding = (yExtent[1] - yExtent[0]) * 0.05

  const baseXScale = d3.scaleLinear()
    .domain([xExtent[0] - xPadding, xExtent[1] + xPadding])
    .range([0, width])

  const baseYScale = d3.scaleLinear()
    .domain([yExtent[0] - yPadding, yExtent[1] + yPadding])
    .range([height, 0])

  // Store original domains for reset
  originalXDomain = baseXScale.domain()
  originalYDomain = baseYScale.domain()

  // Get current zoom transform
  const transform = d3.zoomTransform(svg.node()) || d3.zoomIdentity

  // Apply zoom transform to scales
  xScale = transform.rescaleX(baseXScale)
  yScale = transform.rescaleY(baseYScale)

  // Update axes
  g.select(".x-axis")
    .transition()
    .duration(500)
    .call(d3.axisBottom(xScale).tickFormat(d3.format(".2f")))

  g.select(".y-axis")
    .transition()
    .duration(500)
    .call(d3.axisLeft(yScale).tickFormat(d3.format(".2f")))

  // Update points
  const circles = g.select(".points-container")
    .selectAll(".point")
    .data(data, d => d.annotation_id)

  circles.exit()
    .transition()
    .duration(300)
    .attr("r", 0)
    .remove()

  const circlesEnter = circles.enter()
    .append("circle")
    .attr("class", "point")
    .attr("r", 0)
    .attr("fill", d => getColor(d.class_name))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .style("opacity", 0.7)
    .style("cursor", "pointer")

  circlesEnter.merge(circles)
    .transition()
    .duration(500)
    .attr("r", 3)
    .attr("cx", d => xScale(d.x))
    .attr("cy", d => yScale(d.y))
    .attr("fill", d => getColor(d.class_name))

  // Add hover effects
  g.selectAll(".point")
    .on("mouseover", function(event, d) {
      d3.select(this)
        .transition()
        .duration(100)
        .attr("r", 5)
        .style("opacity", 1)
        .attr("stroke-width", 1)
    })
    .on("mouseout", function(event, d) {
      d3.select(this)
        .transition()
        .duration(100)
        .attr("r", 3)
        .style("opacity", 0.7)
        .attr("stroke-width", 0.5)
    })
}

function handleZoom(event) {
  const { transform } = event

  // Update scales with zoom transform
  if (originalXDomain && originalYDomain) {
    const baseXScale = d3.scaleLinear().domain(originalXDomain).range([0, width])
    const baseYScale = d3.scaleLinear().domain(originalYDomain).range([height, 0])
    
    xScale = transform.rescaleX(baseXScale)
    yScale = transform.rescaleY(baseYScale)

    // Update axes
    g.select(".x-axis").call(d3.axisBottom(xScale).tickFormat(d3.format(".2f")))
    g.select(".y-axis").call(d3.axisLeft(yScale).tickFormat(d3.format(".2f")))

    // Update points positions
    g.selectAll(".point")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
  }
}

function resetZoom() {
  svg.transition()
    .duration(750)
    .call(zoom.transform, d3.zoomIdentity)
}

function handleBrushEnd(event) {
  const selection = event.selection
  if (!selection) {
    dataStore.clearSelection()
    // Clear selection highlighting
    g.selectAll(".point").classed("selected", false)
    return
  }

  const [[x0, y0], [x1, y1]] = selection
  
  // Convert pixel coordinates to data coordinates using current scales
  const dataCoords = {
    x_min: xScale.invert(x0),
    x_max: xScale.invert(x1),
    y_min: yScale.invert(y1), // Note: y coordinates are inverted
    y_max: yScale.invert(y0)
  }

  // Highlight selected points
  g.selectAll(".point")
    .classed("selected", d => 
      d.x >= dataCoords.x_min && d.x <= dataCoords.x_max &&
      d.y >= dataCoords.y_min && d.y <= dataCoords.y_max
    )

  // Update store with selection
  dataStore.updateSelection(dataCoords)
}

onMounted(() => {
  // Wait for next tick to ensure container is rendered
  nextTick(() => {
    initChart()
    setupResizeObserver()
  })
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  } else {
    window.removeEventListener('resize', handleResize)
  }
  clearTimeout(resizeTimeout)
})

watch(() => dataStore.filteredEmbeddings, () => {
  if (svg) {
    updateChart()
  }
}, { deep: true })

watch(() => dataStore.selectedClass, () => {
  if (dataStore.selectedClass === 'all') {
    dataStore.loadEmbeddings()
  } else {
    dataStore.loadClassEmbeddings(dataStore.selectedClass)
  }
})

// Watch for visibility changes (useful for tabs, modals, etc.)
watch(() => chartRef.value, (newRef) => {
  if (newRef && svg) {
    // Re-check dimensions in case container became visible
    nextTick(() => {
      const oldWidth = width
      const oldHeight = height
      updateDimensions()
      
      if (width !== oldWidth || height !== oldHeight) {
        resizeChart()
      }
    })
  }
})
</script>

<style scoped>
.scatter-plot-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 300px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chart {
  flex: 1;
  width: 100%;
  height: 100%;
  min-height: 0; /* Important for flex child to shrink */
  cursor: crosshair;
  overflow: hidden;
}

.plot-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-top: 1px solid #eee;
  background: #f9f9f9;
  border-radius: 0 0 8px 8px;
}

.reset-button {
  padding: 4px 12px;
  font-size: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  color: #666;
  cursor: pointer;
  transition: all 0.2s ease;
}

.reset-button:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #ccc;
}

.reset-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.controls-info {
  font-size: 11px;
  color: #888;
  font-style: italic;
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

/* D3 specific styles */
:deep(.point.selected) {
  stroke: #ff6600 !important;
  stroke-width: 2px !important;
  filter: drop-shadow(0 0 3px rgba(255, 102, 0, 0.8));
}

:deep(.brush .selection) {
  fill: rgba(255, 102, 0, 0.2);
  stroke: #ff6600;
  stroke-width: 1px;
}

:deep(.axis) {
  font-size: 11px;
}

:deep(.axis path),
:deep(.axis line) {
  fill: none;
  stroke: #333;
  shape-rendering: crispEdges;
}

:deep(.axis text) {
  fill: #333;
}

/* Zoom cursors */
.chart:deep(svg) {
  cursor: crosshair;
}

.chart:deep(svg):active {
  cursor: move;
}

@media (max-width: 768px) {
  .plot-controls {
    flex-direction: column;
    gap: 4px;
    padding: 6px;
  }
  
  .controls-info {
    font-size: 10px;
    text-align: center;
  }
}
</style>