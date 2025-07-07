import json
import numpy as np
from typing import Dict, List, Optional
import os
from pathlib import Path

class DataLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.embeddings: Optional[np.ndarray] = None
        self.annotations: Optional[dict] = None
        self.mapping: Optional[Dict[int, int]] = None  # annotation_id -> embedding_index
        self.class_names: List[str] = []
        
    def load_all(self):
        """Load all required data files"""
        self.load_embeddings()
        self.load_annotations()
        self.load_mapping()
        self._extract_class_names()
        
    def load_embeddings(self):
        """Load embeddings from numpy file"""
        embeddings_path = self.data_dir / "embeddings_2d.npy"
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings file not found: {embeddings_path}")
        
        self.embeddings = np.load(embeddings_path)
        print(f"Loaded embeddings: {self.embeddings.shape}")
        
    def load_annotations(self):
        """Load COCO annotations"""
        annotations_path = self.data_dir / "annotations.json"
        if not annotations_path.exists():
            raise FileNotFoundError(f"Annotations file not found: {annotations_path}")
            
        with open(annotations_path, 'r') as f:
            self.annotations = json.load(f)
        print(f"Loaded {len(self.annotations.get('annotations', []))} annotations")
        
    def load_mapping(self):
        """Load annotation_id to embedding index mapping"""
        mapping_path = self.data_dir / "mapping.json"
        if not mapping_path.exists():
            raise FileNotFoundError(f"Mapping file not found: {mapping_path}")
            
        with open(mapping_path, 'r') as f:
            mapping_data = json.load(f)
            
        # Convert string keys to int if necessary
        self.mapping = {int(k): v for k, v in mapping_data.items()}
        print(f"Loaded mapping for {len(self.mapping)} annotations")
        
    def _extract_class_names(self):
        """Extract unique class names from annotations"""
        if not self.annotations:
            return
            
        # Get category names from COCO categories
        categories = self.annotations.get('categories', [])
        self.class_names = [cat['name'] for cat in categories]
        
        # If no categories, extract from annotations directly
        if not self.class_names and 'annotations' in self.annotations:
            category_ids = set()
            for ann in self.annotations['annotations']:
                category_ids.add(ann.get('category_id'))
            self.class_names = [f"class_{cid}" for cid in sorted(category_ids)]
            
        print(f"Found {len(self.class_names)} classes: {self.class_names}")
        
    def get_embedding_points(self, class_filter: Optional[str] = None) -> List[dict]:
        """Get embedding points with class information"""
        if self.embeddings is None or self.annotations is None or self.mapping is None:
            raise RuntimeError("Data not loaded. Call load_all() first.")
        
        points = []
        
        # Create category_id to name mapping
        cat_id_to_name = {}
        if 'categories' in self.annotations:
            cat_id_to_name = {cat['id']: cat['name'] for cat in self.annotations['categories']}
        
        for annotation in self.annotations['annotations']:
            annotation_id = annotation['id']
            category_id = annotation.get('category_id')
            
            # Get class name
            if cat_id_to_name:
                class_name = cat_id_to_name.get(category_id, f"class_{category_id}")
            else:
                class_name = f"class_{category_id}"
                
            # Skip if class filter is applied and doesn't match
            if class_filter and class_filter != class_name:
                continue
                
            # Get embedding index
            if annotation_id not in self.mapping:
                continue
                
            embedding_idx = self.mapping[annotation_id]
            if embedding_idx >= len(self.embeddings):
                continue
                
            # Get 2D coordinates
            x, y = self.embeddings[embedding_idx]
            
            points.append({
                'annotation_id': annotation_id,
                'x': float(x),
                'y': float(y),
                'class_name': class_name
            })
            
        return points
        
    def get_annotations_in_selection(self, x_min: float, x_max: float, 
                                   y_min: float, y_max: float) -> List[int]:
        """Get annotation IDs within the selection rectangle"""
        points = self.get_embedding_points()
        
        selected_ids = []
        for point in points:
            if (x_min <= point['x'] <= x_max and 
                y_min <= point['y'] <= y_max):
                selected_ids.append(point['annotation_id'])
                
        return selected_ids
        
    def get_annotation_by_id(self, annotation_id: int) -> Optional[dict]:
        """Get annotation data by ID"""
        if not self.annotations:
            return None
            
        for annotation in self.annotations['annotations']:
            if annotation['id'] == annotation_id:
                return annotation
        return None
        
    def remove_annotations(self, annotation_ids: List[int]) -> str:
        """Remove annotations and save to new file"""
        if not self.annotations:
            raise RuntimeError("Annotations not loaded")
            
        # Filter out the annotations to remove
        original_count = len(self.annotations['annotations'])
        self.annotations['annotations'] = [
            ann for ann in self.annotations['annotations']
            if ann['id'] not in annotation_ids
        ]
        
        removed_count = original_count - len(self.annotations['annotations'])
        
        # Save to filtered annotations directory
        output_dir = self.data_dir / "filtered_annotations"
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"filtered_annotations_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.annotations, f, indent=2)
            
        print(f"Removed {removed_count} annotations, saved to {output_file}")
        return str(output_file)

# Global data loader instance
data_loader = DataLoader()