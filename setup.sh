#!/bin/bash

# Create Object Detection Analysis Tool project structure
echo "🚀 Creating Object Detection Analysis Tool project structure..."

# Create main directories
mkdir -p backend/{api,models,services}
mkdir -p frontend/{src/{components,services,stores,styles},public}
mkdir -p data/{images,filtered_annotations}

# Backend files
touch backend/__init__.py
touch backend/main.py
touch backend/requirements.txt
touch backend/start_server.py

# Backend API
touch backend/api/__init__.py
touch backend/api/embeddings.py
touch backend/api/images.py
touch backend/api/annotations.py

# Backend Models
touch backend/models/__init__.py
touch backend/models/data_models.py

# Backend Services
touch backend/services/__init__.py
touch backend/services/data_loader.py
touch backend/services/image_service.py
touch backend/services/coco_service.py

# Frontend root files
touch frontend/package.json
touch frontend/vite.config.js
touch frontend/index.html

# Frontend src
touch frontend/src/main.js
touch frontend/src/App.vue

# Frontend components
touch frontend/src/components/ScatterPlot.vue
touch frontend/src/components/Gallery.vue
touch frontend/src/components/ImageItem.vue
touch frontend/src/components/ClassSelector.vue
touch frontend/src/components/RemoveButton.vue

# Frontend services and stores
touch frontend/src/services/api.js
touch frontend/src/stores/useDataStore.js
touch frontend/src/styles/main.css

# Create sample data files with minimal content
echo "Creating sample data files..."

# Sample embeddings (empty numpy array placeholder)
cat > data/embeddings.npy << 'EOF'
# This is a placeholder for embeddings.npy
# Replace with your actual numpy array file containing 2D embeddings
# Shape should be (N, 2) where N is number of detections
EOF

# Sample COCO annotations
cat > data/annotations.json << 'EOF'
{
  "info": {
    "description": "Object Detection Predictions",
    "version": "1.0",
    "year": 2024
  },
  "images": [],
  "annotations": [],
  "categories": [
    {"id": 1, "name": "person", "supercategory": "person"},
    {"id": 2, "name": "bicycle", "supercategory": "vehicle"},
    {"id": 3, "name": "car", "supercategory": "vehicle"},
    {"id": 4, "name": "motorcycle", "supercategory": "vehicle"},
    {"id": 5, "name": "airplane", "supercategory": "vehicle"}
  ]
}
EOF

# Sample mapping file
cat > data/mapping.json << 'EOF'
{
  "_comment": "Maps annotation_id to embedding index",
  "_example": {
    "12345": 0,
    "12346": 1,
    "12347": 2
  }
}
EOF

# Root files
touch README.md

# Create placeholder image
echo "Creating placeholder image..."
cat > data/images/.gitkeep << 'EOF'
# Place your original images here
# Supported formats: .jpg, .jpeg, .png, .bmp, .tiff
EOF

# Create gitkeep for filtered annotations
cat > data/filtered_annotations/.gitkeep << 'EOF'
# Filtered annotation files will be saved here with timestamps
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build outputs
frontend/dist/
frontend/build/

# Data files (uncomment to ignore large data files)
# data/embeddings.npy
# data/images/*
# !data/images/.gitkeep

# Logs
*.log
logs/

# Environment variables
.env
.env.local
.env.production
EOF