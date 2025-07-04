# Object Detection Analysis Tool

An interactive web application for analyzing and cleaning object detection predictions using 2D embeddings visualization.

## Features

- 🎯 **Interactive Scatter Plot**: Visualize object detection embeddings in 2D space with D3.js
- 🖼️ **Detection Gallery**: View cropped detection regions in a scrollable gallery
- 🎨 **Class-based Filtering**: Filter visualizations by object class
- ✅ **Batch Selection**: Select multiple detections using rectangular selection
- 🗑️ **Outlier Removal**: Remove incorrect predictions and export cleaned annotations
- 📊 **Real-time Updates**: Responsive interface with live data synchronization

## Architecture

```
Frontend (Vue.js + D3.js)  ←→  Backend (FastAPI)
├── Interactive scatter plot      ├── Embedding data serving
├── Detection gallery            ├── Image cropping service  
├── Class selector              ├── COCO annotation handling
└── Removal interface           └── Data persistence
```

## Setup Instructions

### Prerequisites

- **Frontend**: Node.js 16+ and npm
- **Backend**: Python 3.8+ and pip
- **Data**: Embeddings, COCO annotations, and image files

### Data Structure

Your data directory should be organized as follows:

```
data/
├── embeddings.npy          # 2D embedding vectors (N x 2)
├── annotations.json        # COCO format predictions  
├── mapping.json           # annotation_id → embedding_index mapping
├── images/                # Original images directory
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── filtered_annotations/   # Output directory (auto-created)
```

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data files:**
   - Place `embeddings.npy`, `annotations.json`, and `mapping.json` in `data/`
   - Ensure `data/images/` contains your original images
   - Verify mapping.json format: `{"annotation_id": embedding_index, ...}`

4. **Start the backend server:**
   ```bash
   python start_server.py
   ```
   
   Or manually:
   ```bash
   python main.py
   ```

   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## Usage Guide

### 1. Initial View
- The scatter plot shows all detection embeddings colored by class
- Use the class dropdown to filter by specific object classes
- The right panel shows detection statistics

### 2. Selecting Detections
- Click and drag on the scatter plot to create a rectangular selection
- Selected points will be highlighted in orange
- The gallery will populate with cropped detection images

### 3. Reviewing Detections
- Scroll through the gallery to examine cropped detections
- Check the boxes for detections you want to remove
- The remove button shows the count of selected items

### 4. Removing Outliers
- Click "Remove X items" to delete selected detections
- Confirm the removal in the dialog
- A new filtered annotation file will be saved with timestamp

### 5. Per-Class Analysis
- Select a specific class from the dropdown for focused analysis
- This helps when dealing with large datasets or specific class issues

## API Endpoints

The FastAPI backend provides these main endpoints:

- `GET /api/embeddings` - Get all embedding points
- `GET /api/embeddings/{class_name}` - Get embeddings for specific class
- `GET /api/classes` - Get available class names
- `POST /api/selection` - Get annotation IDs in selection rectangle
- `GET /api/crop/{annotation_id}` - Get cropped detection image
- `POST /api/remove` - Remove annotations by IDs
- `GET /health` - Check system health

Full API documentation: `http://localhost:8000/docs`

## File Formats

### Embeddings (embeddings.npy)
```python
# Shape: (N, 2) where N is number of detections
# Each row: [x_coordinate, y_coordinate]
embeddings = np.array([[0.1, 0.5], [0.3, 0.2], ...])
```

### Mapping (mapping.json)
```json
{
  "annotation_id": embedding_index,
  "12345": 0,
  "12346": 1,
  "12347": 2
}
```

### COCO Annotations (annotations.json)
Standard COCO format with:
- `annotations`: List of detection annotations
- `images`: Image metadata
- `categories`: Class definitions

## Troubleshooting

### Backend Issues

**"Data files not found":**
- Ensure `data/embeddings.npy`, `data/annotations.json`, and `data/mapping.json` exist
- Check file permissions and paths

**"Images not loading":**
- Verify `data/images/` directory exists with image files
- Check that image filenames in COCO annotations match actual files
- Supported formats: .jpg, .jpeg, .png, .bmp, .tiff

**"Mapping errors":**
- Ensure all annotation IDs in mapping.json exist in annotations.json
- Verify embedding indices are within bounds of embeddings.npy

### Frontend Issues

**"Cannot connect to backend":**
- Confirm backend is running on `http://localhost:8000`
- Check CORS settings if accessing from different port

**"Scatter plot not displaying":**
- Verify embeddings data is being served correctly: `http://localhost:8000/api/embeddings`
- Check browser console for JavaScript errors

## Development

### Backend Development
- Use `python main.py` for basic serving
- Use `python start_server.py` for startup checks and data validation
- API docs available at `http://localhost:8000/docs`

### Frontend Development
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## License

This project is open source and available under the MIT License.