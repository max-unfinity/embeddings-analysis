import json
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from .data_loader import data_loader

class COCOService:
    def __init__(self):
        pass
        
    def get_categories(self) -> List[Dict]:
        """Get all categories from COCO annotations"""
        if not data_loader.annotations:
            return []
        return data_loader.annotations.get('categories', [])
        
    def get_category_names(self) -> List[str]:
        """Get list of category names"""
        categories = self.get_categories()
        return [cat['name'] for cat in categories]
        
    def validate_annotation_ids(self, annotation_ids: List[int]) -> List[int]:
        """Validate that annotation IDs exist and return valid ones"""
        if not data_loader.annotations:
            return []
            
        existing_ids = {ann['id'] for ann in data_loader.annotations['annotations']}
        return [aid for aid in annotation_ids if aid in existing_ids]
        
    def remove_annotations_by_ids(self, annotation_ids: List[int]) -> Dict:
        """Remove annotations by IDs and return summary"""
        if not data_loader.annotations:
            raise RuntimeError("Annotations not loaded")
            
        # Validate annotation IDs
        valid_ids = self.validate_annotation_ids(annotation_ids)
        
        # Count before removal
        original_count = len(data_loader.annotations['annotations'])
        
        # Remove annotations
        data_loader.annotations['annotations'] = [
            ann for ann in data_loader.annotations['annotations']
            if ann['id'] not in valid_ids
        ]
        
        new_count = len(data_loader.annotations['annotations'])
        removed_count = original_count - new_count
        
        # Save to new file
        output_file = self._save_filtered_annotations()
        
        return {
            'success': True,
            'removed_count': removed_count,
            'requested_count': len(annotation_ids),
            'valid_count': len(valid_ids),
            'output_file': output_file
        }
        
    def _save_filtered_annotations(self) -> str:
        """Save current annotations to a new filtered file"""
        # Create output directory
        output_dir = Path("data/filtered_annotations")
        output_dir.mkdir(exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"filtered_annotations_{timestamp}.json"
        
        # Save annotations
        with open(output_file, 'w') as f:
            json.dump(data_loader.annotations, f, indent=2)
            
        return str(output_file)
        
    def get_annotation_stats(self) -> Dict:
        """Get statistics about current annotations"""
        if not data_loader.annotations:
            return {}
            
        annotations = data_loader.annotations['annotations']
        
        # Count by category
        category_counts = {}
        for ann in annotations:
            cat_id = ann.get('category_id')
            category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
            
        # Map category IDs to names
        categories = {cat['id']: cat['name'] for cat in self.get_categories()}
        named_counts = {
            categories.get(cat_id, f"category_{cat_id}"): count 
            for cat_id, count in category_counts.items()
        }
        
        return {
            'total_annotations': len(annotations),
            'category_counts': named_counts,
            'total_categories': len(category_counts),
            'total_images': len(data_loader.annotations.get('images', []))
        }

# Global COCO service instance
coco_service = COCOService()