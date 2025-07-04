<template>
  <div class="scatter-plot-container">
    <div ref="chartRef" class="chart"></div>
    <div v-if="dataStore.loading" class="loading-overlay">
      Loading embeddings...
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { useDataStore } from '../stores/useDataStore'

const chartRef = ref(null)
const dataStore = useDataStore()

let svg, xScale, yScale, brush

const margin = { top: 20, right: 20, bottom: 40, left: 40 }
const width = 600 - margin.left - margin.right
const height = 500 - margin.top - margin.bottom

// Class colors mapping
const classColors = {
  'person': '#e41a1c',
  'bicycle': '#377eb8',
  'car': '#4daf4a',
  'motorcycle': '#984ea3',
  'airplane': '#ff7f00',
  'bus': '#ffff33',
  'train': '#a65628',
  'truck': '#f781bf',
  'boat': '#999999',
  'default': '#1f77b4'
}

function getColor(className) {
  return classColors[className] || classColors.default
}

function initChart() {
  // Clear existing chart
  d3.select(chartRef.value).selectAll("*").remove()

  svg = d3.select(chartRef.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)

  const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`)

  // Add axes groups
  g.append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0,${height})`)

  g.append("g")
    .attr("class", "y-axis")

  // Add brush for selection
  brush = d3.brush()
    .extent([[0, 0], [width, height]])
    .on("end", handleBrushEnd)

  g.append("g")
    .attr("class", "brush")
    .call(brush)
}

function updateChart() {
  if (!svg || !dataStore.filteredEmbeddings.length) return

  const data = dataStore.filteredEmbeddings

  // Update scales
  xScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.x))
    .range([0, width])

  yScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.y))
    .range([height, 0])

  // Update axes
  const g = svg.select("g")
  
  g.select(".x-axis")
    .transition()
    .duration(500)
    .call(d3.axisBottom(xScale))

  g.select(".y-axis")
    .transition()
    .duration(500)
    .call(d3.axisLeft(yScale))

  // Update points
  const circles = g.selectAll(".point")
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
    .attr("cx", d => xScale(d.x))
    .attr("cy", d => yScale(d.y))
    .attr("fill", d => getColor(d.class_name))
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5)
    .style("opacity", 0.7)

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
    })
    .on("mouseout", function(event, d) {
      d3.select(this)
        .transition()
        .duration(100)
        .attr("r", 3)
        .style("opacity", 0.7)
    })
}

function handleBrushEnd(event) {
  const selection = event.selection
  if (!selection) {
    dataStore.clearSelection()
    return
  }

  const [[x0, y0], [x1, y1]] = selection
  
  // Convert pixel coordinates to data coordinates
  const dataCoords = {
    x_min: xScale.invert(x0),
    x_max: xScale.invert(x1),
    y_min: yScale.invert(y1), // Note: y coordinates are inverted
    y_max: yScale.invert(y0)
  }

  // Highlight selected points
  svg.selectAll(".point")
    .classed("selected", d => 
      d.x >= dataCoords.x_min && d.x <= dataCoords.x_max &&
      d.y >= dataCoords.y_min && d.y <= dataCoords.y_max
    )

  // Update store with selection
  dataStore.updateSelection(dataCoords)
}

onMounted(() => {
  initChart()
})

watch(() => dataStore.filteredEmbeddings, () => {
  updateChart()
}, { deep: true })

watch(() => dataStore.selectedClass, () => {
  if (dataStore.selectedClass === 'all') {
    dataStore.loadEmbeddings()
  } else {
    dataStore.loadClassEmbeddings(dataStore.selectedClass)
  }
})
</script>

<style scoped>
.scatter-plot-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 500px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
}

.chart {
  width: 100%;
  height: 100%;
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

:deep(.point.selected) {
  stroke: #ff6600 !important;
  stroke-width: 2px !important;
  r: 4 !important;
}

:deep(.brush .selection) {
  fill: rgba(255, 102, 0, 0.2);
  stroke: #ff6600;
  stroke-width: 1px;
}
</style>